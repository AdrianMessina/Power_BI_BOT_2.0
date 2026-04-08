"""
Analizador de Código DAX
Analiza medidas DAX y proporciona insights sobre complejidad, funciones y performance
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class DAXAnalysis:
    """Resultado del análisis de código DAX"""
    complexity_score: int  # 0-100
    complexity_level: str  # 'Low', 'Medium', 'High', 'Very High'
    functions_used: List[str]
    tables_referenced: List[str]
    measures_referenced: List[str]
    columns_referenced: List[str]
    has_variables: bool
    has_iterators: bool
    has_time_intelligence: bool
    estimated_performance: str  # 'Good', 'Fair', 'Poor'
    performance_warnings: List[str]
    performance_tips: List[str]
    line_count: int
    char_count: int


class DAXAnalyzer:
    """
    Analizador estático de código DAX
    Proporciona insights sobre complejidad, funciones y performance
    """

    # Funciones DAX comunes categorizadas
    AGGREGATION_FUNCTIONS = [
        'SUM', 'AVERAGE', 'MIN', 'MAX', 'COUNT', 'COUNTA', 'COUNTROWS',
        'COUNTBLANK', 'DISTINCTCOUNT', 'COUNTX', 'SUMX', 'AVERAGEX',
        'MINX', 'MAXX'
    ]

    FILTER_FUNCTIONS = [
        'FILTER', 'ALL', 'ALLEXCEPT', 'ALLNOBLANKROW', 'ALLSELECTED',
        'KEEPFILTERS', 'REMOVEFILTERS', 'SELECTEDVALUE', 'VALUES',
        'DISTINCT', 'HASONEVALUE', 'ISFILTERED', 'ISCROSSFILTERED'
    ]

    ITERATOR_FUNCTIONS = [
        'SUMX', 'AVERAGEX', 'COUNTX', 'MINX', 'MAXX', 'PRODUCTX',
        'CONCATENATEX', 'RANKX', 'TOPN'
    ]

    TIME_INTELLIGENCE_FUNCTIONS = [
        'TOTALYTD', 'TOTALQTD', 'TOTALMTD', 'DATESYTD', 'DATESQTD',
        'DATESMTD', 'SAMEPERIODLASTYEAR', 'PARALLELPERIOD', 'DATEADD',
        'DATESBETWEEN', 'DATESINPERIOD', 'PREVIOUSMONTH', 'PREVIOUSQUARTER',
        'PREVIOUSYEAR', 'NEXTMONTH', 'NEXTQUARTER', 'NEXTYEAR',
        'STARTOFMONTH', 'STARTOFQUARTER', 'STARTOFYEAR', 'ENDOFMONTH',
        'ENDOFQUARTER', 'ENDOFYEAR'
    ]

    LOGICAL_FUNCTIONS = [
        'IF', 'IFERROR', 'SWITCH', 'AND', 'OR', 'NOT', 'TRUE', 'FALSE',
        'ISBLANK', 'ISERROR', 'ISLOGICAL', 'ISNUMBER', 'ISTEXT'
    ]

    RELATIONSHIP_FUNCTIONS = [
        'RELATED', 'RELATEDTABLE', 'USERELATIONSHIP', 'CROSSFILTER'
    ]

    CALCULATION_FUNCTIONS = [
        'CALCULATE', 'CALCULATETABLE', 'DIVIDE', 'QUOTIENT', 'MOD',
        'ROUND', 'ROUNDUP', 'ROUNDDOWN', 'INT', 'TRUNC', 'ABS',
        'SIGN', 'SQRT', 'POWER', 'EXP', 'LN', 'LOG', 'LOG10'
    ]

    def __init__(self):
        """Inicializa el analizador"""
        self.all_functions = set()
        for functions in [
            self.AGGREGATION_FUNCTIONS,
            self.FILTER_FUNCTIONS,
            self.ITERATOR_FUNCTIONS,
            self.TIME_INTELLIGENCE_FUNCTIONS,
            self.LOGICAL_FUNCTIONS,
            self.RELATIONSHIP_FUNCTIONS,
            self.CALCULATION_FUNCTIONS
        ]:
            self.all_functions.update(functions)

    def analyze(self, dax_code: str) -> DAXAnalysis:
        """
        Analiza código DAX y retorna insights

        Args:
            dax_code: Código DAX a analizar

        Returns:
            DAXAnalysis con resultados del análisis
        """
        # Limpiar código
        clean_code = self._clean_code(dax_code)

        # Análisis de funciones
        functions_used = self._extract_functions(clean_code)

        # Análisis de referencias
        tables = self._extract_tables(clean_code)
        measures = self._extract_measures(clean_code)
        columns = self._extract_columns(clean_code)

        # Análisis de características
        has_variables = self._has_variables(clean_code)
        has_iterators = self._has_iterators(functions_used)
        has_time_intelligence = self._has_time_intelligence(functions_used)

        # Calcular complejidad
        complexity_score = self._calculate_complexity(
            clean_code, functions_used, has_variables, has_iterators
        )
        complexity_level = self._get_complexity_level(complexity_score)

        # Análisis de performance
        performance, warnings, tips = self._analyze_performance(
            clean_code, functions_used, has_iterators, complexity_score
        )

        # Métricas básicas
        line_count = len(clean_code.split('\n'))
        char_count = len(clean_code)

        return DAXAnalysis(
            complexity_score=complexity_score,
            complexity_level=complexity_level,
            functions_used=functions_used,
            tables_referenced=tables,
            measures_referenced=measures,
            columns_referenced=columns,
            has_variables=has_variables,
            has_iterators=has_iterators,
            has_time_intelligence=has_time_intelligence,
            estimated_performance=performance,
            performance_warnings=warnings,
            performance_tips=tips,
            line_count=line_count,
            char_count=char_count
        )

    def _clean_code(self, code: str) -> str:
        """Limpia el código DAX para análisis"""
        # Remover comentarios de línea
        code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
        # Remover comentarios de bloque
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        return code.strip()

    def _extract_functions(self, code: str) -> List[str]:
        """Extrae funciones DAX usadas en el código"""
        functions = []
        code_upper = code.upper()

        for func in self.all_functions:
            # Buscar función seguida de paréntesis
            pattern = r'\b' + re.escape(func) + r'\s*\('
            if re.search(pattern, code_upper):
                functions.append(func)

        return sorted(functions)

    def _extract_tables(self, code: str) -> List[str]:
        """Extrae referencias a tablas"""
        # Buscar patrones: Tabla[Columna] o 'Tabla'[Columna]
        pattern = r"(?:'([^']+)'|(\w+))\["
        matches = re.findall(pattern, code)

        tables = set()
        for match in matches:
            table_name = match[0] if match[0] else match[1]
            if table_name:
                tables.add(table_name)

        return sorted(list(tables))

    def _extract_measures(self, code: str) -> List[str]:
        """Extrae referencias a medidas"""
        # Buscar patrones: [MeasureName]
        pattern = r'\[([^\[\]]+)\]'
        matches = re.findall(pattern, code)

        # Filtrar columnas (que tienen tabla delante)
        measures = []
        for match in matches:
            # Si no tiene punto y no está después de una tabla, es medida
            if '.' not in match and not re.search(r'\w+\[' + re.escape(match) + r'\]', code):
                measures.append(match)

        return sorted(list(set(measures)))

    def _extract_columns(self, code: str) -> List[str]:
        """Extrae referencias a columnas"""
        # Buscar patrones: Tabla[Columna]
        pattern = r"(?:'([^']+)'|(\w+))\[([^\]]+)\]"
        matches = re.findall(pattern, code)

        columns = set()
        for match in matches:
            table = match[0] if match[0] else match[1]
            column = match[2]
            if table and column:
                columns.add(f"{table}[{column}]")

        return sorted(list(columns))

    def _has_variables(self, code: str) -> bool:
        """Detecta si usa variables VAR"""
        return bool(re.search(r'\bVAR\b', code, re.IGNORECASE))

    def _has_iterators(self, functions: List[str]) -> bool:
        """Detecta si usa funciones iteradoras"""
        return any(func in self.ITERATOR_FUNCTIONS for func in functions)

    def _has_time_intelligence(self, functions: List[str]) -> bool:
        """Detecta si usa funciones de time intelligence"""
        return any(func in self.TIME_INTELLIGENCE_FUNCTIONS for func in functions)

    def _calculate_complexity(
        self,
        code: str,
        functions: List[str],
        has_variables: bool,
        has_iterators: bool
    ) -> int:
        """
        Calcula score de complejidad (0-100)
        """
        score = 0

        # Base: longitud del código
        lines = len(code.split('\n'))
        score += min(lines * 2, 20)  # Max 20 puntos

        # Número de funciones
        score += min(len(functions) * 3, 30)  # Max 30 puntos

        # Uso de variables
        if has_variables:
            var_count = len(re.findall(r'\bVAR\b', code, re.IGNORECASE))
            score += min(var_count * 5, 15)  # Max 15 puntos

        # Iteradores (más costosos)
        if has_iterators:
            score += 10

        # Anidamiento de funciones
        nesting_level = self._calculate_nesting_level(code)
        score += min(nesting_level * 5, 15)  # Max 15 puntos

        # Funciones CALCULATE anidadas
        calculate_count = code.upper().count('CALCULATE')
        if calculate_count > 1:
            score += min(calculate_count * 3, 10)  # Max 10 puntos

        return min(score, 100)

    def _calculate_nesting_level(self, code: str) -> int:
        """Calcula nivel máximo de anidamiento de paréntesis"""
        max_level = 0
        current_level = 0

        for char in code:
            if char == '(':
                current_level += 1
                max_level = max(max_level, current_level)
            elif char == ')':
                current_level -= 1

        return max_level

    def _get_complexity_level(self, score: int) -> str:
        """Convierte score a nivel de complejidad"""
        if score < 25:
            return 'Low'
        elif score < 50:
            return 'Medium'
        elif score < 75:
            return 'High'
        else:
            return 'Very High'

    def _analyze_performance(
        self,
        code: str,
        functions: List[str],
        has_iterators: bool,
        complexity: int
    ) -> Tuple[str, List[str], List[str]]:
        """
        Analiza performance esperado y genera warnings/tips

        Returns:
            (performance_level, warnings, tips)
        """
        warnings = []
        tips = []

        # Performance base según complejidad
        if complexity < 40:
            performance = 'Good'
        elif complexity < 70:
            performance = 'Fair'
        else:
            performance = 'Poor'

        # Advertencias específicas
        if has_iterators:
            iterator_count = sum(1 for f in functions if f in self.ITERATOR_FUNCTIONS)
            if iterator_count > 2:
                warnings.append("Múltiples iteradores pueden afectar el rendimiento")
                tips.append("Considera usar variables para almacenar resultados de iteradores")

        if 'FILTER' in functions:
            filter_count = code.upper().count('FILTER(')
            if filter_count > 2:
                warnings.append("Uso intensivo de FILTER puede ser costoso")
                tips.append("Evalúa usar CALCULATE con filtros en lugar de FILTER cuando sea posible")

        if code.upper().count('CALCULATE') > 3:
            warnings.append("Múltiples CALCULATE anidados detectados")
            tips.append("Simplifica usando variables para almacenar contextos de filtro")

        if 'RELATED' in functions:
            tips.append("RELATED es eficiente para relaciones uno-a-muchos")

        if 'ALL' in functions and 'CALCULATE' in functions:
            tips.append("Combinar ALL con CALCULATE puede ser costoso en tablas grandes")

        # Tips generales según complejidad
        if complexity > 60:
            tips.append("Considera dividir esta medida en medidas más simples")
            tips.append("Usa variables (VAR) para mejorar legibilidad y performance")

        if not warnings:
            tips.append("La medida tiene buena estructura")

        return performance, warnings, tips

    def get_function_categories(self, functions: List[str]) -> Dict[str, List[str]]:
        """
        Categoriza funciones usadas

        Args:
            functions: Lista de funciones a categorizar

        Returns:
            Dict con categorías y funciones
        """
        categories = {
            'Aggregation': [],
            'Filter': [],
            'Iterator': [],
            'Time Intelligence': [],
            'Logical': [],
            'Relationship': [],
            'Calculation': [],
            'Other': []
        }

        for func in functions:
            if func in self.AGGREGATION_FUNCTIONS:
                categories['Aggregation'].append(func)
            elif func in self.FILTER_FUNCTIONS:
                categories['Filter'].append(func)
            elif func in self.ITERATOR_FUNCTIONS:
                categories['Iterator'].append(func)
            elif func in self.TIME_INTELLIGENCE_FUNCTIONS:
                categories['Time Intelligence'].append(func)
            elif func in self.LOGICAL_FUNCTIONS:
                categories['Logical'].append(func)
            elif func in self.RELATIONSHIP_FUNCTIONS:
                categories['Relationship'].append(func)
            elif func in self.CALCULATION_FUNCTIONS:
                categories['Calculation'].append(func)
            else:
                categories['Other'].append(func)

        # Remover categorías vacías
        return {k: v for k, v in categories.items() if v}

    def explain_measure(self, analysis: DAXAnalysis, measure_name: str) -> str:
        """
        Genera explicación en lenguaje natural de lo que hace la medida

        Args:
            analysis: Resultado del análisis
            measure_name: Nombre de la medida

        Returns:
            Explicación en texto
        """
        explanation = f"**{measure_name}** es una medida "

        # Complejidad
        if analysis.complexity_level == 'Low':
            explanation += "simple "
        elif analysis.complexity_level == 'Medium':
            explanation += "de complejidad media "
        elif analysis.complexity_level == 'High':
            explanation += "compleja "
        else:
            explanation += "muy compleja "

        # Tipo de medida según funciones
        if analysis.has_time_intelligence:
            explanation += "de **time intelligence** "
        elif analysis.has_iterators:
            explanation += "que **itera sobre filas** "
        elif 'CALCULATE' in analysis.functions_used:
            explanation += "que **modifica el contexto de filtro** "
        elif any(f in analysis.functions_used for f in ['SUM', 'AVERAGE', 'COUNT']):
            explanation += "de **agregación** "

        # Referencias
        if analysis.tables_referenced:
            explanation += f"que referencia {len(analysis.tables_referenced)} tabla(s) "

        if analysis.measures_referenced:
            explanation += f"y usa {len(analysis.measures_referenced)} medida(s) base "

        explanation += "."

        return explanation
