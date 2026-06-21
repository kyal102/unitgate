import unittest
from unitgate import check_equation, VALID, INVALID, AMBIGUOUS, MALFORMED


class TestUnitGate(unittest.TestCase):
    def test_newton_second_law_is_valid(self):
        self.assertEqual(check_equation("F = m * a").status, VALID)

    def test_energy_equals_mass_times_acceleration_is_invalid(self):
        r = check_equation("E = m * a")
        self.assertEqual(r.status, INVALID)
        self.assertNotEqual(r.lhs_dim, r.rhs_dim)

    def test_mass_energy_is_valid(self):
        self.assertEqual(check_equation("E = m * c**2").status, VALID)

    def test_momentum_is_valid(self):
        self.assertEqual(check_equation("p = m * v").status, VALID)

    def test_velocity_distance_over_time_is_valid(self):
        self.assertEqual(check_equation("v = d / t").status, VALID)

    def test_word_forms(self):
        self.assertEqual(check_equation("power = energy / time").status, VALID)

    def test_force_equals_mass_times_velocity_is_invalid(self):
        self.assertEqual(check_equation("F = m * v").status, INVALID)

    def test_unknown_symbol_is_ambiguous(self):
        self.assertEqual(check_equation("E = zzz * a").status, AMBIGUOUS)

    def test_malformed(self):
        self.assertEqual(check_equation("E m a").status, MALFORMED)
        self.assertEqual(check_equation("E = m = a").status, MALFORMED)


if __name__ == "__main__":
    unittest.main()
