import subprocess
class Term:
    """
    Klasse zur Repraesentation von logischen Ausdruecken der Form
    Operator(Term1,Term2), Not(Term), Variable, TOP, BOT

    Attribute: parameters: Liste der Parameter eines Terms, Anzahl der Elemente
                         entspricht der Stelligkeit des Operators

                operator: enthaelt die Art der Verknuepfung eines logischen Ausdrucks
                          2-stellig: Or, And, Biimpl, Impl
                          1-stellig: Not
                          0-stellig: Variable, BOT, TOP

    """
    def __init__(self, operator, parameters=None):
        self.parameters = parameters
        self.operator = operator


class ParserStringToDIMACS:

    @staticmethod
    def build_term_from_string(formula):
        """ Erzeugt für eine Formel im Stringformat,
            welche nach der vorgegebenen Syntax gebildet wurde,
            einen entsprechenden Term

            Argumente: formula: String

            returns: term
    """
        formula = ParserStringToDIMACS.eat_whitespace(formula)
        if len(formula) > 3:
            if formula[:2] == "Or":
                formula = formula[3:len(formula) - 1]
                operator = "Or"
            elif formula[:3] == "And":
                formula = formula[4:len(formula) - 1]
                operator = "And"
            elif formula[:3] == "Not":
                formula = formula[4:len(formula) - 1]
                operator = "Not"
            elif formula[:4] == "Impl":
                formula = formula[5:len(formula) - 1]
                operator = "Impl"
            elif formula[:6] == "BiImpl":
                formula = formula[7:len(formula) - 1]
                operator = "BiImpl"
            else:
                assert False, "No valid formula"

            left_parameter = ""
            right_parameter = ""
            parentheses_count = 0
            for i in range(0, len(formula)):
                if formula[i] == "(":
                    parentheses_count += 1
                elif formula[i] == ")":
                    parentheses_count -= 1
                if formula[i] == "," and parentheses_count == 0:
                    right_parameter = formula[i + 1:len(formula)]
                    break
                left_parameter += formula[i]

            left_parameter_term = ParserStringToDIMACS.build_term_from_string(left_parameter)  # recursion
            if operator == "Not":
                if right_parameter != "":
                    assert False, "No valid formula"
                term = Term(operator, [left_parameter_term])
            else:
                right_parameter_term = ParserStringToDIMACS.build_term_from_string(right_parameter)  # recursion
                term = Term(operator, [left_parameter_term, right_parameter_term])
            return term
        else:
            term = Term(formula, [])
            return term

    @staticmethod
    def eat_whitespace(formula_in_string):
        """ Eliminiert Leerzeichen des Eingabestrings

            Argumente: formula_in_string: String
            returns: String ohne Leerzeichen
        """
        new_formula_in_string = ""
        for i in range(0, len(formula_in_string)):
            if formula_in_string[i] != " ":
                new_formula_in_string += formula_in_string[i]
            else:
                continue
        return new_formula_in_string

    @staticmethod
    def replace_implication(term):
        """ Ersetzt eine Implikation (a -> b) durch (¬a v b)

        :param term: Objekt der Klasse Term
        :return: Term
        """
        if term.operator != "Impl":
            return term
        else:
            new_parameters = [Term("Not", [term.parameters[0]])]
            new_parameters += term.parameters[1:]
            replaced = Term("Or", new_parameters)
            return replaced

    @staticmethod
    def replace_biimplication(term):
        """ Ersetzt eine Biimplikation Biimpl(a, b) durch And(Or(Not(a), b), Or(Not(b), a))

                :param term: Objekt der Klasse Term
                :return: Term
        """
        if term.operator != "BiImpl":
            return term
        else:
            subterm1 = Term("Or", [term.parameters[0], Term("Not", [term.parameters[1]])])
            subterm2 = Term("Or", [term.parameters[1], Term("Not", [term.parameters[0]])])
            replaced = Term("And", [subterm1, subterm2])
            return replaced

    @staticmethod
    def de_morgan(term):
        """ Wendet die De Morgan Regeln auf einen Term an

                        :param term: Objekt der Klasse Term
                        :return: Term
        """
        replaced = term
        if term.operator == "Not":
            if term.parameters[0].operator == "Or":
                replaced = Term(
                    "And",
                    [Term("Not", [term.parameters[0].parameters[0]]), Term("Not", [term.parameters[0].parameters[1]])]
                )
            if term.parameters[0].operator == "And":
                replaced = Term(
                    "Or",
                    [Term("Not", [term.parameters[0].parameters[0]]), Term("Not", [term.parameters[0].parameters[1]])]
                )
            if term.parameters[0].operator == "Not":
                replaced = Term(term.parameters[0].parameters[0].operator, term.parameters[0].parameters[0].parameters)
        return replaced

    @staticmethod
    def is_clause(term):
        """ Ueberprueft, ob ein Term eine Klausel ist

                                :param term: Objekt der Klasse Term
                                :return: true, falls Klausel
        """
        operators = ("Or", "And", "Not", "Impl", "BiImpl")
        if term.operator not in operators:
            return True
        elif term.operator == "Not":
            if term.parameters[0].operator not in operators:
                return True
            else:
                return False
        elif term.operator == "Or":
            res = (ParserStringToDIMACS.is_clause(term.parameters[0]) and ParserStringToDIMACS.is_clause(term.parameters[1]))
            return res
        else:
            return False

    @staticmethod
    def apply_distributive_law(term):
        """ Wendet das Distributivgesetz an, um die Disjunktionen nach innen zu ziehen

        :param term:
        :return: term
        """
        if term.operator != "Or":  # hack: wir brauchen nur Or, da And bereits in KNF
            return term
        else:
            if term.parameters[0].operator != "And" and term.parameters[1].operator != "And":
                return term
            # Fall: Or(And(a,b ), And(c, d)
            elif term.parameters[0].operator == "And" and term.parameters[1].operator =="And":
                t1 = Term("Or", [term.parameters[0].parameters[0], term.parameters[1].parameters[0]])
                t2 = Term("Or", [term.parameters[0].parameters[0], term.parameters[1].parameters[1]])
                t3 = Term("Or", [term.parameters[0].parameters[1], term.parameters[1].parameters[0]])
                t4 = Term("Or", [term.parameters[0].parameters[1], term.parameters[1].parameters[1]])
                and1 = Term("And", [t1, t2])
                and2 = Term("And", [t3, t4])
                return Term("And", [and1, and2])
            # Fall: Or(And(a,b ), c)
            elif term.parameters[0].operator == "And" and term.parameters[1].operator != "And":
                t1 = Term("Or", [term.parameters[0].parameters[0], term.parameters[1]])
                t2 = Term("Or", [term.parameters[0].parameters[1], term.parameters[1]])
                return Term("And", [t1, t2])
            # Fall: Or(c, And(a,b))
            elif term.parameters[0].operator != "And" and term.parameters[1].operator == "And":
                t1 = Term("Or", [term.parameters[1].parameters[0], term.parameters[0]])
                t2 = Term("Or", [term.parameters[1].parameters[1], term.parameters[0]])
                return Term("And", [t1, t2])

    @staticmethod
    def convert_to_cnf(term):
        """ Wandelt einen Term durch Anwendung von Umformungsregeln (De Morgan, Distributivgesetz,
            Umwandlung von Implikation/Biimplikation in Terme mit Or/And Verknuepfung)
            in Konjunktive Normalform(KNF) um

        :param term:
        :return: term in KNF
        """
        if term.operator == "Or":
            # wandle Parameter des Terms rekursiv in KNF um
            parameter0 = ParserStringToDIMACS.convert_to_cnf(term.parameters[0])
            parameter1 = ParserStringToDIMACS.convert_to_cnf(term.parameters[1])
            # Pruefe, ob der Term aequivalent ist zu TOP
            if parameter0.operator == "TOP" or parameter1.operator == "TOP":
                return Term("TOP", [])
            # entferne redundante BOT Parameter
            if parameter0.operator == "BOT":
                return parameter1
            if parameter1.operator == "BOT":
                return parameter0
            else:
                result = Term("Or", [parameter0, parameter1])
                # Distributivgesetz, um das Or reinzuziehen
                result = ParserStringToDIMACS.apply_distributive_law(result)
                return result
        elif term.operator == "Impl":
            # wandle Parameter des Terms rekursiv in KNF um
            parameter0 = ParserStringToDIMACS.convert_to_cnf(term.parameters[0])
            parameter1 = ParserStringToDIMACS.convert_to_cnf(term.parameters[1])
            # Pruefe, ob der Term aequivalent ist zu TOP
            if parameter0.operator == "BOT" or parameter1.operator == "TOP":
                return Term("TOP", [])
            # entferne redundante Parameter
            if parameter0.operator == "TOP":
                return parameter1
            if parameter1.operator == "BOT":
                return ParserStringToDIMACS.convert_to_cnf(Term('Not', [parameter0]))
            result = Term("Impl", [parameter0, parameter1])
            result = ParserStringToDIMACS.replace_implication(result)
            return ParserStringToDIMACS.convert_to_cnf(result)
        elif term.operator == "BiImpl":
            # wandle Parameter des Terms rekursiv in KNF um
            parameter0 = ParserStringToDIMACS.convert_to_cnf(term.parameters[0])
            parameter1 = ParserStringToDIMACS.convert_to_cnf(term.parameters[1])
            # Pruefe, ob der Term aequivalent ist zu TOP
            if parameter0.operator == "BOT" and parameter1.operator == "BOT":
                return Term("TOP", [])
            if parameter0.operator == "TOP" and parameter1.operator == "TOP":
                return Term("TOP", [])
            # entferne redundante Parameter
            if parameter0.operator == "TOP":
                return parameter1
            if parameter1.operator == "TOP":
                return parameter0
            # Wenn einer der Parameter BOT ist,
            # dann entspricht der Term dem invertierten anderen Parameter
            if parameter0.operator == "BOT":
                return ParserStringToDIMACS.convert_to_cnf(Term('Not', [parameter1]))
            if parameter1.operator == "BOT":
                return ParserStringToDIMACS.convert_to_cnf(Term('Not', [parameter0]))
            result = Term("BiImpl", [parameter0, parameter1])
            result = ParserStringToDIMACS.replace_biimplication(result)
            return ParserStringToDIMACS.convert_to_cnf(result)
        elif term.operator == "And":
            # wandle Parameter des Terms rekursiv in KNF um
            parameter0 = ParserStringToDIMACS.convert_to_cnf(term.parameters[0])
            parameter1 = ParserStringToDIMACS.convert_to_cnf(term.parameters[1])
            # entferne redundante Parameter
            if parameter0.operator == "TOP":
                return parameter1
            if parameter1.operator == "TOP":
                return parameter0
            # Pruefe, ob der Term aequivalent ist zu BOT
            if parameter0.operator == "BOT" or parameter1.operator == "BOT":
                return Term("BOT", [])
            else:
                result = Term("And", [parameter0, parameter1])
                return result
        elif term.operator == "Not":
            # Pruefe, ob der Term aequivalentyu TOP/BOT ist
            if term.parameters[0].operator == "BOT":
                return Term("TOP", [])
            if term.parameters[0].operator == "TOP":
                return Term("BOT", [])
            # De Morgan bei Termen mit Or/ And
            if term.parameters[0].operator == "And" or term.parameters[0].operator == "Or":
                result = ParserStringToDIMACS.de_morgan(term)
                result = ParserStringToDIMACS.convert_to_cnf(result)
                return result
            # eliminiere doppelte Verneinung
            elif term.parameters[0].operator == "Not":
                return ParserStringToDIMACS.convert_to_cnf(term.parameters[0].parameters[0])
            # wandle verneinte Implikation in And (term1, not term2) um
            elif term.parameters[0].operator == "Impl":
                result = Term(
                    "And",
                    [term.parameters[0].parameters[0], Term("Not", [term.parameters[0].parameters[1]])]
                )
                return ParserStringToDIMACS.convert_to_cnf(result)
            # wandle verneinte BiImpl in Or(not term 1, not term 2) um
            elif term.parameters[0].operator == "BiImpl":
                rep = ParserStringToDIMACS.replace_biimplication(term.parameters[0])
                t1 = Term("Not", [rep.parameters[0]])
                t2 = Term("Not", [rep.parameters[1]])
                res = Term("Or", [t1, t2])
                return ParserStringToDIMACS.convert_to_cnf(res)
            else:
                return term
        else:
            return term

    @staticmethod
    def build_pre_dimacs_string(term_in_cnf):
        """ Erzeugt aus einem Objekt der Klasse Term in KNF eine Stringrepräsentation ähnlich  dem DIMACS Format,
            wobei die Variablen noch nicht durch Ziffern ersetzt wurden und die Kopfzeile "p cnf numvar numclauses"
            fehlt. Jede Zeile entspricht einer Klausel, die Leerzeichen zwischen den Variablen entsprechen
            dem Junktor AND, - enspricht NOT.

                :param term_in_cnf: Objekt der Klasse Term
                :return: String
                """
        output = ""
        if term_in_cnf.operator == "Or":
            for x in term_in_cnf.parameters:
                if x.operator == "Or":
                    res = ParserStringToDIMACS.build_pre_dimacs_string(x)
                    output += res
                elif x.operator == "Not":
                    variable = x.parameters[0].operator
                    res = "-" + variable
                    output += res
                    output += " "
                else:
                    output += x.operator
                    output += " "
        # And bedeutet, dass (mind.) zwei Klauseln gefunden wurden, d
        # aher werden diese durch einen Zeilenumbruch getrennt
        elif term_in_cnf.operator == "And":
            res1 = ParserStringToDIMACS.build_pre_dimacs_string(term_in_cnf.parameters[0])
            res2 = ParserStringToDIMACS.build_pre_dimacs_string(term_in_cnf.parameters[1])
            output += res1 + "\n"
            output += res2
        else:
            if term_in_cnf.operator == "Not":
                variable = term_in_cnf.parameters[0].operator
                res = "-" + variable
                output += res
                # output += " 0"
            else:
                output += term_in_cnf.operator
                # output += " 0"
        return output

    @staticmethod
    def create_dimacs(term_in_cnf):
        """ Erzeugt aus einem Objekt der Klasse Term in KNF eine Stringausgabe im DIMACS Format. Der Term wird zunächst
            mittels build_string in ein Stringformat gebracht, in dem jede Klausel in einer Zeile steht und die
            Operatoren And und Not jeweils durch Leerzeichen bzw. Minuszeichen repräsentiert werden.
            Dieser wird dann in das DIMACS Format gebracht

                        :param term_in_cnf: Objekt der Klasse Term
                        :return: DIMACS-String
        """
        # Dictionary, das jeder Variablen eine Zahl zuordnet
        variable_number_by_name = {}
        # da der Term  mindestens eine Klausel enthält und bei einer einzelnen Klausel kein Zeilenumbruch im String
        # erfolgt, starten wir bei 1
        num_clauses = 1
        num_variables = 0
        current_number = 1
        # erstelle den vorläufigen Dimacs String
        term_in_cnf = ParserStringToDIMACS.build_pre_dimacs_string(term_in_cnf)
        # Zeilenumbruch = neue Klausel
        for x in term_in_cnf:
            if x == "\n":
                num_clauses += 1
            elif x == "-" or x == " " or x == "0":
                continue
            else:
                # Erstelle einen neuen Eintrag im Dictionary, falls x nicht vorhanden
                if x not in variable_number_by_name:
                    variable_number_by_name[x] = current_number
                    current_number += 1
                    num_variables += 1
        # Füge die Kopfzeile des DIMAC Formats hinzu
        dimacs = "p cnf " + str(num_variables) + " " + str(num_clauses) + "\n"
        # Bilde DIMACS durch ersetzten der Variablen durch die entsprechenden Zahlen
        for i in range(0, len(term_in_cnf)):
            y = term_in_cnf[i]
            # Füge eine 0 an das Ende jeder Zeile hinzu
            if y == "\n":
                if term_in_cnf[i - 1] != " ":
                    dimacs += " "
                dimacs += "0"
            if y in variable_number_by_name:
                y = variable_number_by_name[y]
            dimacs += str(y)
            # Füge eine 0 am Ende der letzten Zeile hinzu
            if i == len(term_in_cnf) - 1:
                if term_in_cnf[i] != " ":
                    dimacs += " "
                dimacs += "0"
        return dimacs

    @staticmethod
    def convert_formula_to_dimacs(formula, stabalize):
        """ Erzeugt für eine Formel im Stringformat ,
            welche nach der vorgegebenen Syntax gebildet wurde, eine Ausgabe im DIMACS Format

                              :param formula: String
                              :param stabalize:

                              :return: DIMACS-String
              """
        formula_term = ParserStringToDIMACS.build_term_from_string(formula)
        #if stabalize:
          #  formula_term = ParserStringToDIMACS.stabilize_formula(formula_term)
        formula_term_in_cnf = ParserStringToDIMACS.convert_to_cnf(formula_term)
        if formula_term_in_cnf.operator == "BOT":
            raise Exception("Formula in CNF is BOT, no dmacs exists ")
        if formula_term_in_cnf.operator == "TOP":
            raise Exception("Formula in CNF is TOP, no dmacs exists ")
        return ParserStringToDIMACS.create_dimacs(formula_term_in_cnf)

    def get_all_models(formula, stabalize):
        """ Erzeugt eine Textdatei "allmodels" für eine gegebene Formel f, die alle Modelle von f enthält.

                                      :param formula: String
                                      :param stabalize:

                                      :return: DIMACS-String
        """

        sat = True
        allmodels = open("allmodels", "w+")
        cnf = ParserStringToDIMACS.convert_formula_to_dmacs(formula, stabalize)
        file = open("problem.cnf", "w+")
        file.write(cnf)
        file.close()
        while sat:
            subprocess.run(["minisat", "problem.cnf", "problem.model"])
            modelfile = open("problem.model", "r")
            result = modelfile.read()
            modelfile.close()
            if result[0:3] != "SAT":
                sat = False
                allmodels.close()
                break
            newmodel = result[4:]
            allmodels.write(newmodel)
            extension_clause = ""
            for i in range(0, len(newmodel)):
                if newmodel[i] == "\n" or newmodel[i] == " " or newmodel[i] == "0":
                    extension_clause += newmodel[i]
                elif newmodel[i] == "-":
                    continue
                else:
                    if i > 0:
                        if newmodel[i - 1] == "-":
                            extension_clause += newmodel[i]
                        else:
                            extension_clause += "-" + newmodel[i]
                    else:
                        extension_clause += "-" + newmodel[i]
            file = open("problem.cnf", "r")
            old_cnf = file.read()
            file.close()
            number_of_clauses = int(old_cnf[8]) + 1
            file = open("problem.cnf", "w+")
            file.write(old_cnf[:8] + str(number_of_clauses) + old_cnf[9:] + "\n" + extension_clause)
            file.close()
