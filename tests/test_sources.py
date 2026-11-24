"""Offline tests of the data modules (companies, DVF, Légifrance)."""

import unittest
from unittest import mock

from fr_open_data import companies, dvf, http, legifrance, municipalities

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

    def test_naf_code_in_text_and_municipality_name(self):
        with mock.patch.object(companies, "request_json", return_value={"results": [], "total_results": 0}) as m, \
                mock.patch.object(municipalities, "request_json", return_value=GEO_DIJON):
            r = companies.search("62.02A", municipality="Dijon")
        params = m.call_args[0][1]
        self.assertEqual((params["q"], params["activite_principale"], params["code_commune"]), ("", "62.02A", "21231"))
        self.assertEqual(r["filters"]["code_commune"], "21231")
        self.assertIn("0 companies match", r["count"])
        self.assertIn("NAF code", r["notes"][0])

    def test_search_filters(self):
        with mock.patch.object(companies, "request_json", return_value={"results": [], "total_results": 0}) as m:
            companies.search(municipality_code="31555", naf_code="62.01z, 62.02A", activity_section="j")
        params = m.call_args[0][1]
        self.assertEqual(params["code_commune"], "31555")
        self.assertEqual(params["activite_principale"], "62.01Z,62.02A")
        self.assertEqual(params["section_activite_principale"], "J")
        self.assertEqual(params["q"], "")
        for bad in ({"municipality_code": "Toulouse"}, {"activity_section": "Z"}, {"naf_code": "informatique"}):
            with self.assertRaises(ValueError):
                companies.search(**bad)


def row(tx, type_code, area=0, value=200000, nature="Vente", parcel="P1", lot=None, rooms=0):
    labels = {1: "Maison", 2: "Appartement", 3: "Dépendance", 4: "Local industriel. commercial ou assimilé"}
    return {"id_mutation": tx, "date_mutation": "2025-03-01", "nature_mutation": nature,
            "valeur_fonciere": value, "id_parcelle": parcel, "lot1_numero": lot,
            "code_type_local": type_code, "type_local": labels.get(type_code),
            "surface_reelle_bati": area, "nombre_pieces_principales": rooms, "nom_commune": "Example"}


GEO_DIJON = [{"nom": "Dijon", "code": "21231", "codeDepartement": "21", "population": 160000},
             {"nom": "Fontaine-lès-Dijon", "code": "21278", "codeDepartement": "21", "population": 9000}]
GEO_HOMONYMS = [{"nom": "Saint-Denis", "code": "97411", "codeDepartement": "974", "population": 150000},
                {"nom": "Saint-Denis", "code": "93066", "codeDepartement": "93", "population": 110000}]


class TestMunicipalities(unittest.TestCase):
    def test_search_is_ranked_by_population(self):
        with mock.patch.object(municipalities, "request_json", return_value=[]) as m:
            municipalities.find("Paris")
        self.assertEqual(m.call_args[0][1]["boost"], "population")

    def test_arrondissements_by_name(self):
        for name, code in (("Paris 11e", "75111"), ("Paris 11e arrondissement", "75111"),
                           ("11e arrondissement de Paris", "75111"), ("Lyon 3", "69383"),
                           ("Marseille 1er arrondissement", "13201"), ("PARIS 20ème", "75120")):
            self.assertEqual(municipalities.arrondissement_code(name), code, name)
        for name in ("Paris", "Paris 21e", "Lyon 10e", "Toulouse 2e"):
            self.assertIsNone(municipalities.arrondissement_code(name), name)

    def test_find_keeps_exact_matches(self):
        with mock.patch.object(municipalities, "request_json", return_value=GEO_DIJON):
            r = municipalities.find("dijon")
        self.assertEqual([x["insee_code"] for x in r["results"]], ["21231"])

    def test_resolve(self):
        with mock.patch.object(municipalities, "request_json", return_value=GEO_DIJON):
            self.assertEqual(municipalities.resolve("Dijon")[:2], ("21231", "Dijon"))
            with self.assertRaisesRegex(ValueError, "Closest names: Dijon"):
                municipalities.resolve("Dijonville")
        with mock.patch.object(municipalities, "request_json", return_value=GEO_HOMONYMS):
            code, _, note = municipalities.resolve("Saint Denis")
            self.assertEqual(code, "97411")  # most populated
            self.assertIn("93066", note)
            self.assertEqual(municipalities.resolve("Saint-Denis", "93066")[0], "93066")


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
        self.assertEqual(s["apartment"]["sales_kept"], 0)
        self.assertNotIn("median_price_per_m2_eur", s["apartment"])
        self.assertIn("no apartment figure", s["apartment"]["note"])

    def test_rejected_codes_offline(self):
        for code, expected in (("75056", 'municipality="Paris <number>e arrondissement"'), ("67482", "Alsace"), ("abc", "INSEE"),
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


class TestDvfReading(unittest.TestCase):
    ROWS = [row("m1", 2, 50, 150000)]

    def test_export_is_used(self):
        with mock.patch.object(dvf, "request_json", return_value=self.ROWS) as m:
            rows, complete = dvf.read_rows("rid", "21054")
        self.assertEqual((rows, complete), (self.ROWS, True))
        self.assertTrue(m.call_args[0][0].endswith("/data/json/"))
        self.assertEqual(m.call_count, 1)

    def test_too_long_export_falls_back_to_pages(self):
        too_long = dvf.SourceError("Output is too long", 403)
        page = {"data": self.ROWS, "links": {"next": "more"}}
        with mock.patch.object(dvf, "request_json", side_effect=[too_long] + [page] * dvf.MAX_PAGES):
            rows, complete = dvf.read_rows("rid", "21054")
        self.assertEqual(len(rows), dvf.MAX_PAGES)
        self.assertFalse(complete)

    def test_other_errors_are_raised(self):
        with mock.patch.object(dvf, "request_json", side_effect=dvf.SourceError("down", 503)):
            with self.assertRaises(dvf.SourceError):
                dvf.read_rows("rid", "21054")

    def _prices(self, **kwargs):
        periods = {"2025": ("rid", "DVF 2025")}
        with mock.patch.object(dvf, "resources_by_period", return_value=periods), \
                mock.patch.object(dvf, "read_rows", return_value=(self.ROWS, True)) as rows, \
                mock.patch.object(municipalities, "request_json", return_value=GEO_DIJON):
            r = dvf.property_prices(period="2025", **kwargs)
        return r, rows.call_args[0][1]

    def test_municipality_name(self):
        r, code = self._prices(municipality="Dijon")
        self.assertEqual((code, r["insee_code"]), ("21231", "21231"))
        r, code = self._prices(municipality="Dijon", insee_code="21054")  # wrong code: the name wins
        self.assertEqual(code, "21231")
        self.assertIn("21054 was not used", r["notes"][0])
        r, code = self._prices(municipality="Paris 11e arrondissement")
        self.assertEqual(code, "75111")

    def test_paris_postcode(self):
        r, code = self._prices(insee_code="75011")
        self.assertEqual(code, "75111")
        self.assertIn("Paris postcode", r["notes"][0])

    def test_partial_data_warning(self):
        periods = {"2025": ("rid", "DVF 2025")}
        with mock.patch.object(dvf, "resources_by_period", return_value=periods), \
                mock.patch.object(dvf, "read_rows", return_value=(self.ROWS, False)):
            r = dvf.property_prices("21054", "2025")
        self.assertFalse(r["complete_data"])
        self.assertIn("Partial data", r["warning"])


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
