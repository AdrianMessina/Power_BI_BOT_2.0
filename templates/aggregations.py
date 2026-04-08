"""
Templates de Agregaciones para Power BI
SUM, AVG, COUNT, MIN, MAX, DISTINCTCOUNT, etc.
"""

from typing import List
from .base_template import BaseTemplateCollection, DAXTemplate, TemplateParameter


class AggregationTemplates(BaseTemplateCollection):
    """Colección de templates de agregaciones"""

    def _load_templates(self):
        """Carga todos los templates de agregaciones"""

        # SUM - Suma simple
        self.templates.append(DAXTemplate(
            id="sum",
            name="Sum",
            description="Suma simple de una columna",
            category="Aggregations",
            difficulty="basic",
            parameters=[
                TemplateParameter(
                    name="measure_name",
                    description="Nombre de la nueva medida",
                    type="text",
                    required=True
                ),
                TemplateParameter(
                    name="table_column",
                    description="Tabla y columna (ej: Ventas[Importe])",
                    type="column",
                    required=True
                )
            ],
            dax_template="""{measure_name} = SUM({table_column})""",
            example="""Total Ventas = SUM(Ventas[Importe])""",
            tags=["sum", "suma", "total", "agregación"],
            requires_date_table=False
        ))

        # AVERAGE - Promedio
        self.templates.append(DAXTemplate(
            id="average",
            name="Average",
            description="Calcula el promedio de una columna",
            category="Aggregations",
            difficulty="basic",
            parameters=[
                TemplateParameter(
                    name="measure_name",
                    description="Nombre de la nueva medida",
                    type="text",
                    required=True
                ),
                TemplateParameter(
                    name="table_column",
                    description="Tabla y columna",
                    type="column",
                    required=True
                )
            ],
            dax_template="""{measure_name} = AVERAGE({table_column})""",
            example="""Precio Promedio = AVERAGE(Productos[Precio])""",
            tags=["average", "promedio", "media", "avg"],
            requires_date_table=False
        ))

        # COUNT - Conteo
        self.templates.append(DAXTemplate(
            id="count",
            name="Count",
            description="Cuenta el número de valores (incluyendo duplicados)",
            category="Aggregations",
            difficulty="basic",
            parameters=[
                TemplateParameter(
                    name="measure_name",
                    description="Nombre de la nueva medida",
                    type="text",
                    required=True
                ),
                TemplateParameter(
                    name="table_column",
                    description="Tabla y columna",
                    type="column",
                    required=True
                )
            ],
            dax_template="""{measure_name} = COUNT({table_column})""",
            example="""Total Transacciones = COUNT(Ventas[TransactionID])""",
            tags=["count", "conteo", "cantidad"],
            requires_date_table=False
        ))

        # DISTINCTCOUNT - Conteo único
        self.templates.append(DAXTemplate(
            id="distinctcount",
            name="Distinct Count",
            description="Cuenta el número de valores únicos",
            category="Aggregations",
            difficulty="basic",
            parameters=[
                TemplateParameter(
                    name="measure_name",
                    description="Nombre de la nueva medida",
                    type="text",
                    required=True
                ),
                TemplateParameter(
                    name="table_column",
                    description="Tabla y columna",
                    type="column",
                    required=True
                )
            ],
            dax_template="""{measure_name} = DISTINCTCOUNT({table_column})""",
            example="""Clientes Únicos = DISTINCTCOUNT(Ventas[ClienteID])""",
            tags=["distinctcount", "unique", "único", "distintos"],
            requires_date_table=False
        ))

        # MIN - Mínimo
        self.templates.append(DAXTemplate(
            id="min",
            name="Minimum",
            description="Obtiene el valor mínimo de una columna",
            category="Aggregations",
            difficulty="basic",
            parameters=[
                TemplateParameter(
                    name="measure_name",
                    description="Nombre de la nueva medida",
                    type="text",
                    required=True
                ),
                TemplateParameter(
                    name="table_column",
                    description="Tabla y columna",
                    type="column",
                    required=True
                )
            ],
            dax_template="""{measure_name} = MIN({table_column})""",
            example="""Precio Mínimo = MIN(Productos[Precio])""",
            tags=["min", "mínimo", "menor"],
            requires_date_table=False
        ))

        # MAX - Máximo
        self.templates.append(DAXTemplate(
            id="max",
            name="Maximum",
            description="Obtiene el valor máximo de una columna",
            category="Aggregations",
            difficulty="basic",
            parameters=[
                TemplateParameter(
                    name="measure_name",
                    description="Nombre de la nueva medida",
                    type="text",
                    required=True
                ),
                TemplateParameter(
                    name="table_column",
                    description="Tabla y columna",
                    type="column",
                    required=True
                )
            ],
            dax_template="""{measure_name} = MAX({table_column})""",
            example="""Precio Máximo = MAX(Productos[Precio])""",
            tags=["max", "máximo", "mayor"],
            requires_date_table=False
        ))

        # SUMX - Suma iterativa
        self.templates.append(DAXTemplate(
            id="sumx",
            name="Sum X (Iterative)",
            description="Suma el resultado de una expresión evaluada fila por fila",
            category="Aggregations",
            difficulty="intermediate",
            parameters=[
                TemplateParameter(
                    name="measure_name",
                    description="Nombre de la nueva medida",
                    type="text",
                    required=True
                ),
                TemplateParameter(
                    name="table",
                    description="Tabla sobre la que iterar",
                    type="table",
                    required=True
                ),
                TemplateParameter(
                    name="expression",
                    description="Expresión a evaluar (ej: [Cantidad] * [Precio])",
                    type="text",
                    required=True
                )
            ],
            dax_template="""{measure_name} =
SUMX(
    {table},
    {expression}
)""",
            example="""Total Ventas =
SUMX(
    Ventas,
    Ventas[Cantidad] * Ventas[Precio]
)""",
            tags=["sumx", "iterative", "iterativo", "suma expresión"],
            requires_date_table=False
        ))

        # AVERAGEX - Promedio iterativo
        self.templates.append(DAXTemplate(
            id="averagex",
            name="Average X (Iterative)",
            description="Promedio del resultado de una expresión evaluada fila por fila",
            category="Aggregations",
            difficulty="intermediate",
            parameters=[
                TemplateParameter(
                    name="measure_name",
                    description="Nombre de la nueva medida",
                    type="text",
                    required=True
                ),
                TemplateParameter(
                    name="table",
                    description="Tabla sobre la que iterar",
                    type="table",
                    required=True
                ),
                TemplateParameter(
                    name="expression",
                    description="Expresión a evaluar",
                    type="text",
                    required=True
                )
            ],
            dax_template="""{measure_name} =
AVERAGEX(
    {table},
    {expression}
)""",
            example="""Margen Promedio =
AVERAGEX(
    Ventas,
    Ventas[Precio] - Ventas[Costo]
)""",
            tags=["averagex", "promedio iterativo", "average expression"],
            requires_date_table=False
        ))

        # COUNTROWS - Contar filas
        self.templates.append(DAXTemplate(
            id="countrows",
            name="Count Rows",
            description="Cuenta el número de filas en una tabla",
            category="Aggregations",
            difficulty="basic",
            parameters=[
                TemplateParameter(
                    name="measure_name",
                    description="Nombre de la nueva medida",
                    type="text",
                    required=True
                ),
                TemplateParameter(
                    name="table",
                    description="Tabla a contar",
                    type="table",
                    required=True
                )
            ],
            dax_template="""{measure_name} = COUNTROWS({table})""",
            example="""Total Ventas = COUNTROWS(Ventas)""",
            tags=["countrows", "contar filas", "rows"],
            requires_date_table=False
        ))

        # COUNTA - Contar no vacíos
        self.templates.append(DAXTemplate(
            id="counta",
            name="Count Non-Blank",
            description="Cuenta valores no vacíos (incluye texto y números)",
            category="Aggregations",
            difficulty="basic",
            parameters=[
                TemplateParameter(
                    name="measure_name",
                    description="Nombre de la nueva medida",
                    type="text",
                    required=True
                ),
                TemplateParameter(
                    name="table_column",
                    description="Tabla y columna",
                    type="column",
                    required=True
                )
            ],
            dax_template="""{measure_name} = COUNTA({table_column})""",
            example="""Comentarios con Texto = COUNTA(Tickets[Comentario])""",
            tags=["counta", "non-blank", "no vacíos"],
            requires_date_table=False
        ))

        # COUNTBLANK - Contar vacíos
        self.templates.append(DAXTemplate(
            id="countblank",
            name="Count Blank",
            description="Cuenta valores vacíos en una columna",
            category="Aggregations",
            difficulty="basic",
            parameters=[
                TemplateParameter(
                    name="measure_name",
                    description="Nombre de la nueva medida",
                    type="text",
                    required=True
                ),
                TemplateParameter(
                    name="table_column",
                    description="Tabla y columna",
                    type="column",
                    required=True
                )
            ],
            dax_template="""{measure_name} = COUNTBLANK({table_column})""",
            example="""Tickets Sin Asignar = COUNTBLANK(Tickets[AsignadoA])""",
            tags=["countblank", "blank", "vacíos", "nulls"],
            requires_date_table=False
        ))

        # Weighted Average
        self.templates.append(DAXTemplate(
            id="weighted_avg",
            name="Weighted Average",
            description="Calcula un promedio ponderado",
            category="Aggregations",
            difficulty="intermediate",
            parameters=[
                TemplateParameter(
                    name="measure_name",
                    description="Nombre de la nueva medida",
                    type="text",
                    required=True
                ),
                TemplateParameter(
                    name="table",
                    description="Tabla sobre la que iterar",
                    type="table",
                    required=True
                ),
                TemplateParameter(
                    name="value_column",
                    description="Columna con valores",
                    type="column",
                    required=True
                ),
                TemplateParameter(
                    name="weight_column",
                    description="Columna con pesos",
                    type="column",
                    required=True
                )
            ],
            dax_template="""{measure_name} =
DIVIDE(
    SUMX({table}, {value_column} * {weight_column}),
    SUM({weight_column})
)""",
            example="""Precio Promedio Ponderado =
DIVIDE(
    SUMX(Ventas, Ventas[Precio] * Ventas[Cantidad]),
    SUM(Ventas[Cantidad])
)""",
            tags=["weighted", "ponderado", "promedio ponderado", "average"],
            requires_date_table=False
        ))

        # Median (Mediana usando PERCENTILE)
        self.templates.append(DAXTemplate(
            id="median",
            name="Median",
            description="Calcula la mediana (percentil 50) de una columna",
            category="Aggregations",
            difficulty="intermediate",
            parameters=[
                TemplateParameter(
                    name="measure_name",
                    description="Nombre de la nueva medida",
                    type="text",
                    required=True
                ),
                TemplateParameter(
                    name="table_column",
                    description="Tabla y columna",
                    type="column",
                    required=True
                )
            ],
            dax_template="""{measure_name} =
PERCENTILE.INC({table_column}, 0.5)""",
            example="""Precio Mediano =
PERCENTILE.INC(Productos[Precio], 0.5)""",
            tags=["median", "mediana", "percentile", "percentil"],
            requires_date_table=False
        ))
