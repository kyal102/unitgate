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

    # ── sums, parentheses, unary minus (v0.2 parser) ──
    def test_kinetic_plus_potential_is_valid(self):
        self.assertEqual(check_equation("E = 0.5*m*v**2 + m*g*h").status, VALID)

    def test_kinematics_sum_is_valid(self):
        self.assertEqual(check_equation("d = v*t + 0.5*a*t**2").status, VALID)

    def test_sum_of_unlike_terms_is_invalid(self):
        r = check_equation("E = m*g*h + m*v")
        self.assertEqual(r.status, INVALID)
        self.assertIn("do not share one dimension", r.reason)

    def test_parentheses_are_supported(self):
        self.assertEqual(check_equation("F = m*(v/t)").status, VALID)
        self.assertEqual(check_equation("v = (d + d) / t").status, VALID)

    def test_parenthesised_power(self):
        self.assertEqual(check_equation("E = m*(d/t)**2").status, VALID)

    def test_unary_minus_is_valid(self):
        self.assertEqual(check_equation("F = -m*a").status, VALID)

    def test_negative_exponent(self):
        self.assertEqual(check_equation("f = t**-1").status, VALID)

    def test_implicit_multiplication_still_works(self):
        self.assertEqual(check_equation("F = m a").status, VALID)

    def test_missing_paren_is_malformed(self):
        self.assertEqual(check_equation("F = m*(v/t").status, MALFORMED)

    def test_non_integer_exponent_is_malformed(self):
        self.assertEqual(check_equation("E = m*v**1.5").status, MALFORMED)


if __name__ == "__main__":
    unittest.main()
