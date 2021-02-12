#import unittest


#class MyTestCase(unittest.TestCase):
  ##  def test_something(self):
    #    self.assertEqual(True, False)


#if __name__ == '__main__':
#    unittest.main()
from aufgabe1neu import ParserStringToDIMACS, Term


def test_build_term_from_formula():
    p = ParserStringToDIMACS()
    x = "Or(a,b)"
    x = p.build_term_from_string(x)
    assert x.operator == "Or"
    assert len(x.parameters) == 2
    assert x.parameters[0].operator == "a"
    assert x.parameters[1].operator == "b"
    n = "Not(f)"
    n = p.build_term_from_string(n)
    assert n.operator == "Not"
    assert len(n.parameters) == 1
    assert n.parameters[0].operator == "f"
    phi = "And(Or(x,b),y)"
    phi = p.build_term_from_string(phi)
    assert phi.operator == "And"
    assert len(phi.parameters) == 2
    assert phi.parameters[0].operator == "Or"
    assert phi.parameters[1].operator == "y"
    psi = "BiImpl(Or(x,b),y)"
    psi = p.build_term_from_string(psi)
    assert psi.operator == "BiImpl"
    assert len(psi.parameters) == 2
    assert psi.parameters[0].operator == "Or"
    assert psi.parameters[1].operator == "y"
    x = "Impl(Or(a,b),n)"
    x = p.build_term_from_string(x)
    assert x.operator == "Impl"
    assert len(x.parameters) == 2
    assert x.parameters[0].operator == "Or"
    assert x.parameters[1].operator == "n"
    x = "Impl(And(a,b),n)"
    x = p.build_term_from_string(x)
    assert len(x.parameters) == 2
    assert x.parameters[0].operator == "And"
    assert x.parameters[1].operator == "n"
    x = "Impl(Not(a),n)"
    x = p.build_term_from_string(x)
    assert len(x.parameters) == 2
    assert x.parameters[0].operator == "Not"
    assert x.parameters[1].operator == "n"
    assert len(x.parameters[0].parameters) == 1
    x = "Not(Or(a,n))"
    x = p.build_term_from_string(x)
    assert x.parameters[0].operator == "Or"
    assert x.operator == "Not"
    x = "Not(And(a,n))"
    x = p.build_term_from_string(x)
    assert x.parameters[0].operator == "And"
    assert x.operator == "Not"
    x = "Not(Impl(a,n))"
    x = p.build_term_from_string(x)
    assert x.parameters[0].operator == "Impl"
    assert x.operator == "Not"
    x = "Or(And(a,b),And(x,y))"
    x = p.build_term_from_string(x)
    assert x.operator == "Or"
    assert x.parameters[0].operator == "And"
    assert x.parameters[1].operator == "And"
    x = "Or(And(Not(a),b),And(x,y))"
    x = p.build_term_from_string(x)
    assert x.operator == "Or"
    assert x.parameters[0].operator == "And"
    assert x.parameters[1].operator == "And"


def test_replace_implication():
    x = "Impl(a,b)"
    y = ParserStringToDIMACS()
    x = y.build_term_from_string(x)
    x = y.replace_implication(x)
    assert x.operator == "Or"
    assert x.parameters[0].operator == "Not"
    assert x.parameters[0].parameters[0].operator == "a"
    assert x.parameters[1].operator == "b"
    x = "Impl(Not(a),b)"
    x = y.build_term_from_string(x)
    x = y.replace_implication(x)
    assert x.operator == "Or"
    assert x.parameters[0].operator == "Not"
    assert x.parameters[0].parameters[0].operator == "Not"
    assert x.parameters[0].parameters[0].parameters[0].operator == "a"
    assert x.parameters[1].operator == "b"


def test_replace_biimplication():
    x = "BiImpl(a,b)"
    y = ParserStringToDIMACS()
    x = y.build_term_from_string(x)
    x = y.replace_biimplication(x)
    assert x.operator == "And"
    assert x.parameters[0].operator == "Or"
    assert x.parameters[1].operator == "Or"
    assert x.parameters[0].parameters[0].operator == "a"
    assert x.parameters[0].parameters[1].operator == "Not"
    assert x.parameters[0].parameters[1].parameters[0].operator == "b"
    assert x.parameters[1].parameters[0].operator == "b"
    assert x.parameters[1].parameters[1].operator == "Not"
    assert x.parameters[1].parameters[1].parameters[0].operator == "a"


def test_de_morgan():
    x = "Not(Or(a,b))"
    y = ParserStringToDIMACS()
    x = y.build_term_from_string(x)
    x = y.de_morgan(x)
    assert x.operator == "And"
    assert x.parameters[0].operator == "Not"
    assert x.parameters[1].operator == "Not"
    assert x.parameters[0].parameters[0].operator == "a"
    assert x.parameters[1].parameters[0].operator == "b"
    x = "Not(Not(a))"
    x = y.build_term_from_string(x)
    x = y.de_morgan(x)
    assert x.operator == "a"
    x = "Not(And(a,b))"
    x = y.build_term_from_string(x)
    x = y.de_morgan(x)
    assert x.operator == "Or"
    assert x.parameters[0].operator == "Not"
    assert x.parameters[1].operator == "Not"
    assert x.parameters[0].parameters[0].operator == "a"
    assert x.parameters[1].parameters[0].operator == "b"
    x = "Not(Impl(a,b))"
    x = y.build_term_from_string(x)
    assert x.operator == "Not"
    x = y.de_morgan(x)
    assert x.operator == "Not"
    assert x.parameters[0].operator == "Impl"


def test_is_clause():
    x = "Not(Or(a,b))"
    y = ParserStringToDIMACS()
    x = y.build_term_from_string(x)
    b = y.is_clause(x)
    assert False == b
    x = "And(Or(a,b))"
    x = y.build_term_from_string(x)
    b = y.is_clause(x)
    assert False == b
    x = "Or(Or(a,b),v)"
    x = y.build_term_from_string(x)
    b = y.is_clause(x)
    assert True == b
    x = "Or(Or(And(a,b)),v)"
    x = y.build_term_from_string(x)
    b = y.is_clause(x)
    assert False == b


def test_apply_distributive_law():
    y = ParserStringToDIMACS()
    x = "Or(And(a,b),c)"
    x = y.build_term_from_string(x)
    x = y.apply_distributive_law(x)
    assert x.operator == "And"
    assert x.parameters[0].operator == "Or"
    assert x.parameters[0].parameters[0].operator == "a"
    assert x.parameters[0].parameters[1].operator == "c"
    assert x.parameters[1].operator == "Or"
    assert x.parameters[1].parameters[0].operator == "b"
    assert x.parameters[1].parameters[1].operator == "c"
    x = "Or(c,And(a,b))"
    x = y.build_term_from_string(x)
    x = y.apply_distributive_law(x)
    assert x.operator == "And"
    assert x.parameters[0].operator == "Or"
    assert x.parameters[0].parameters[0].operator == "a"
    assert x.parameters[0].parameters[1].operator == "c"
    assert x.parameters[1].operator == "Or"
    assert x.parameters[1].parameters[0].operator == "b"
    assert x.parameters[1].parameters[1].operator == "c"
    x = "Or(And(a,b),And(Impl(a,b),c))"
    x = y.build_term_from_string(x)
    x = y.apply_distributive_law(x)
    assert x.operator == "And"
    assert x.parameters[0].operator == "And"
    assert x.parameters[0].parameters[0].operator == "Or"
    assert x.parameters[0].parameters[1].operator == "Or"
    assert x.parameters[1].parameters[0].operator == "Or"
    assert x.parameters[1].parameters[1].operator == "Or"
    assert x.parameters[0].parameters[0].parameters[0].operator == "a"
    assert x.parameters[0].parameters[0].parameters[1].operator == "Impl"
    assert x.parameters[0].parameters[1].parameters[0].operator == "a"
    assert x.parameters[0].parameters[1].parameters[1].operator == "c"
    assert x.parameters[1].parameters[0].parameters[0].operator == "b"
    assert x.parameters[1].parameters[0].parameters[1].operator == "Impl"
    assert x.parameters[1].parameters[1].parameters[0].operator == "b"
    assert x.parameters[1].parameters[1].parameters[1].operator == "c"


def test_convert_to_cnf():
    y = ParserStringToDIMACS()
    x = "a"
    x = y.build_term_from_string(x)
    x = y.convert_to_cnf(x)
    assert x.operator == "a"
    x = "Or(And(a,b),Impl(c,d))"
    x = y.build_term_from_string(x)
    x = y.convert_to_cnf(x)
    assert x.operator == "And"
    assert x.parameters[0].operator == "Or"
    assert x.parameters[1].operator == "Or"
    assert x.parameters[0].parameters[0].operator == "a"
    assert x.parameters[0].parameters[1].operator == "Or"
    x = "Not(And(a,b))"
    x = y.build_term_from_string(x)
    x = y.convert_to_cnf(x)
    assert x.operator == "Or"
    assert x.parameters[0].operator == "Not"
    assert x.parameters[0].parameters[0].operator == "a"
    assert x.parameters[1].operator == "Not"
    assert x.parameters[1].parameters[0].operator == "b"
    x = "Not(Impl(a,b))"
    x = y.build_term_from_string(x)
    x = y.convert_to_cnf(x)
    assert x.operator == "And"
    assert x.parameters[0].operator == "a"
    assert x.parameters[1].operator == "Not"
    assert x.parameters[1].parameters[0].operator == "b"
    x = "Not(Not(Impl(a,b)))"
    x = y.build_term_from_string(x)
    x = y.convert_to_cnf(x)
    assert x.operator == "Or"
    assert x.parameters[0].operator == "Not"
    assert x.parameters[0].parameters[0].operator == "a"
    assert x.parameters[1].operator == "b"


def test_build_pre_dimacs_string():
    y = ParserStringToDIMACS()
    t = "And (Or(a, b), Or(x, y))"
    t = y.build_term_from_string(t)
    t = y.build_pre_dimacs_string(t)
    assert t[0] == "a"
    assert t[1] == " "
    assert t[2] == "b"
    assert t[3] == " "
    assert t[4] == "\n"
    assert t[5] == "x"
    assert t[6] == " "
    assert t[7] == "y"
    x = "Or(And(a,b),And(x,y))"
    x= y.build_term_from_string(x)
    x = y.convert_to_cnf(x)
    x = y.build_pre_dimacs_string(x)
    assert x[0] == "a"
    assert x[1] == " "
    assert x[2] == "x"



def test_create_dimacs():
    y = ParserStringToDIMACS()
    t = "And (Or(a, b), Or(x, y))"
    t = y.build_term_from_string(t)
    t = y.create_dimacs(t)
    res = "p cnf "






test_build_term_from_formula()
test_replace_implication()
test_replace_biimplication()
test_de_morgan()
test_apply_distributive_law()
test_convert_to_cnf()
test_build_pre_dimacs_string()
