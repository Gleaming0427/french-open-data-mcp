"""Offline tests of the data modules (companies, DVF, Légifrance)."""

import unittest
from unittest import mock

from fr_open_data import companies, dvf, http, legifrance

# Fictitious result in the Recherche d'entreprises API format (made-up names).
FAKE_RESULT = {
    "siren": "123456789",
    "nom_complet": "ATELIERS FICTIFS",
    "sigle": None,
    "etat_administratif": "A",
    "date_creation": "2010-05-01",
    "date_fermeture": None,
    "activite_principale": "25.62B",
    "nature_juridique": "5710",
    "categorie_entreprise": "PME",
    "tranche_effectif_salarie": "12",
    "annee_tranche_effectif_salarie": "2024",
    "nombre_etablissements_ouverts": 2,
    "opposition_diffusion_commerciale": True,
    "siege": {"siret": "12345678900012", "adresse": "1 RUE DE L'EXEMPLE 21000 DIJON",
              "code_postal": "21000", "libelle_commune": "DIJON", "commune": "21231"},
    "dirigeants": [
        {"nom": "DUPONT", "prenoms": "JEANNE", "annee_de_naissance": "1970", "date_de_naissance": "1970-01",
         "qualite": "Président de SAS", "nationalite": "Française", "type_dirigeant": "personne physique"},
        {"siren": "987654321", "denomination": "CABINET FICTIF", "qualite": "Commissaire aux comptes titulaire",
         "type_dirigeant": "personne morale"},
    ],
    "finances": {"2025": {"ca": 1000000, "resultat_net": 50000}},
    "complements": {"liste_idcc": ["3248"], "est_rge": True, "est_bio": False, "est_ess": None},
    "tva": ["FR00123456789"],
}


class TestHttp(unittest.TestCase):
    def _error(self, code):
        import io
        import urllib.error
        return urllib.error.HTTPError("https://example.org", code, "x", {}, io.BytesIO(b'{"detail": "PGRST002"}'))

    def _ok(self):
        resp = mock.MagicMock()
        resp.__enter__.return_value.read.return_value = b'{"data": []}'
        return resp

    @mock.patch("fr_open_data.http.time.sleep")
    def test_unavailable_is_retried_once(self, sleep):
        with mock.patch("urllib.request.urlopen", side_effect=[self._error(503), self._ok()]):
            self.assertEqual(http.request_json("https://example.org"), {"data": []})
        sleep.assert_called_once_with(2.0)
        with mock.patch("urllib.request.urlopen", side_effect=[self._error(503), self._error(503)]):
            with self.assertRaisesRegex(http.SourceError, r"temporarily unavailable \(HTTP 503\).*PGRST002"):
                http.request_json("https://example.org", source_name="Tabular API")

    @mock.patch("fr_open_data.http.time.sleep")
    def test_other_errors_are_not_retried(self, sleep):
        with mock.patch("urllib.request.urlopen", side_effect=[self._error(404)]):
            with self.assertRaisesRegex(http.SourceError, "HTTP 404"):
                http.request_json("https://example.org")
        sleep.assert_not_called()


class TestCompanies(unittest.TestCase):
    def test_siren(self):
        self.assertEqual(companies.normalize_siren("123 456 789"), "123456789")
        self.assertEqual(companies.normalize_siren("12345678900012"), "123456789")
        with self.assertRaises(ValueError):
            companies.normalize_siren("1234")

    def test_summary(self):
        r = companies.summarize(FAKE_RESULT)
        self.assertEqual(r["status"], "active")
        self.assertEqual(r["workforce"], "20 to 49 employees")
        self.assertTrue(r["objects_to_commercial_prospecting"])
        self.assertEqual(r["head_office"]["municipality_code"], "21231")

    def test_profile_has_no_birth_data(self):
        p = companies.profile(FAKE_RESULT)
        person = p["directors"][0]
        self.assertEqual(set(person), {"type", "last_name", "first_names", "role"})
        self.assertEqual(p["directors"][1]["name"], "CABINET FICTIF")
        self.assertEqual(p["labels_and_statuses"], ["est_rge"])
        self.assertEqual(p["vat_number"], "FR00123456789")

    def test_profile_not_found(self):
        with mock.patch.object(companies, "request_json", return_value={"results": []}):
            with self.assertRaises(companies.SourceError):
                companies.get_profile("123456789")

    def test_search_parameters(self):
        with mock.patch.object(companies, "request_json",
                               return_value={"results": [FAKE_RESULT], "total_results": 1}) as m:
            r = companies.search("ateliers", postcode="21000", limit=99)
        params = m.call_args[0][1]
        self.assertEqual(params["per_page"], 25)
        self.assertEqual(params["etat_administratif"], "A")
        self.assertEqual(r["results"][0]["siren"], "123456789")


def row(tx, type_code, area=0, value=200000, nature="Vente", parcel="P1", lot=None, rooms=0):
    labels = {1: "Maison", 2: "Appartement", 3: "Dépendance", 4: "Local industriel. commercial ou assimilé"}
    return {"id_mutation": tx, "date_mutation": "2025-03-01", "nature_mutation": nature,
            "valeur_fonciere": value, "id_parcelle": parcel, "lot1_numero": lot,
            "code_type_local": type_code, "type_local": labels.get(type_code),
            "surface_reelle_bati": area, "nombre_pieces_principales": rooms, "nom_commune": "Example"}


class TestDvf(unittest.TestCase):
    def test_sale_selection(self):
        rows = [
            row("m1", 1, 100, 250000),                                    # single house: kept
            row("m2", 2, 50, 150000, lot="10"), row("m2", 3, lot="11"),
            row("m2", 2, 50, 150000, lot="10"),                           # duplicate + outbuilding: kept
            row("m3", 2, 40, 300000, lot="1"), row("m3", 2, 45, 300000, lot="2"),  # 2 dwellings: dropped
            row("m4", 1, 80, 400000), row("m4", 4, 200, 400000),          # commercial premises: dropped
            row("m5", 1, 90, 180000, nature="Echange"),                   # not a sale: dropped
            row("m6", 1, 0, 100000),                                      # zero area: dropped
            row("m7", None, 0, 50000),                                    # land only: dropped
        ]
        kept, n_sales = dvf.dwelling_sales(rows)
        self.assertEqual(n_sales, 6)
        self.assertEqual(sorted(v["type"] for v in kept), ["apartment", "house"])
        apartment = next(v for v in kept if v["type"] == "apartment")
        self.assertEqual(apartment["price_m2"], 3000)

    def test_statistics(self):
        sales = [{"type": "house", "value": v, "area": 100, "price_m2": v / 100} for v in (100000, 200000, 300000)]
        s = dvf.statistics_by_type(sales)
        self.assertEqual(s["house"]["median_price_per_m2_eur"], 2000)
        self.assertEqual(s["house"]["median_price_eur"], 200000)
        self.assertIn("warning", s["house"])
        self.assertEqual(s["apartment"], {"sales_kept": 0})

    def test_rejected_codes_offline(self):
        for code, expected in (("75056", "arrondissement"), ("67482", "Alsace"), ("abc", "INSEE"),
                               ("97608", "Mayotte")):
            with self.assertRaises(ValueError) as ctx:
                dvf.property_prices(code)
            self.assertIn(expected, str(ctx.exception))

    def test_periods(self):
        dataset = {"resources": [
            {"id": "a", "title": "DVF 2024"}, {"id": "b", "title": "DVF 2025"},
            {"id": "c", "title": "DVF 2026 (1er semestre)"}, {"id": "d", "title": "DVF 2021 (2nd semestre)"},
            {"id": "e", "title": "DVF juillet 2021 - juin 2026 - fichier unique"},
        ]}
        with mock.patch.object(dvf, "request_json", return_value=dataset):
            p = dvf.resources_by_period(force=True)
        self.assertEqual(sorted(p), ["2021-S2", "2024", "2025", "2026-S1"])
        self.assertEqual(dvf.latest_full_year(p), "2025")
        dvf._resource_cache = None


class TestLegifrance(unittest.TestCase):
    def test_search_body(self):
        b = legifrance.search_body("bail commercial", "CODE_DATE", 50)
        self.assertEqual(b["fond"], "CODE_DATE")
        self.assertEqual(b["recherche"]["pageSize"], 20)
        self.assertEqual(b["recherche"]["champs"][0]["criteres"][0]["valeur"], "bail commercial")
        with self.assertRaises(ValueError):
            legifrance.search_body("x", "UNKNOWN", 5)

    def test_defensive_parsing(self):
        response = {"results": [{"titles": [{"id": "LEGITEXT1", "cid": "LEGITEXT1", "title": "Code <mark>civil</mark>"}],
                                 "sections": [{"extracts": [{"id": "LEGIARTI000000000001", "num": "1",
                                                             "values": ["Les <mark>lois</mark> sont..."]}]}]},
                                {"title": "No titles"}]}
        r = legifrance.summarize_results(response)
        self.assertEqual(r[0]["title"], "Code civil")
        self.assertEqual(r[0]["articles"][0]["extract"], "Les lois sont...")
        self.assertEqual(r[1]["title"], "No titles")
        self.assertEqual(legifrance.summarize_results(None), [])

    def test_article_id(self):
        with self.assertRaises(ValueError):
            legifrance.read_article("article 1240")

    def test_not_configured(self):
        with mock.patch.dict("os.environ", {}, clear=True):
            self.assertFalse(legifrance.is_configured())
            with self.assertRaises(legifrance.SourceError):
                legifrance.search("bail")


if __name__ == "__main__":
    unittest.main()
