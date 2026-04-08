"""
Templates de Cálculos para Power BI
Ratios, Porcentajes, Varianzas, Márgenes, etc.
"""

from typing import List
from .base_template import BaseTemplateCollection, DAXTemplate, TemplateParameter


class CalculationTemplates(BaseTemplateCollection):
    """Colección de templates de cálculos"""

    def _load_templates(self):
        """Carga todos los templates de cálculos"""

        # Percentage (Porcentaje simple)
        self.templates.append(DAXTemplate(
            id="percentage",
            name="Percentage",
            description="Calcula el porcentaje de una medida sobre otra",
            category="Calculations",
            difficulty="basic",
            parameters=[
                TemplateParameter(
                    name="measure_name",
                    description="Nombre de la nueva medida",
                    type="text",
                    required=True
                ),
                TemplateParameter(
                    name="numerator",
                    description="Medida numerador",
                    type="measure",
                    required=True
                ),
                TemplateParameter(
                    name="denominator",
                    description="Medida denominador",
                    type="measure",
                    required=True
                )
            ],
            dax_template="""{measure_name} =
DIVIDE(
    [{numerator}],
    [{denominator}]
)""",
            example="""Margen % =
DIVIDE(
    [Utilidad],
    [Ventas]
)""",
            tags=["percentage", "porcentaje", "ratio", "división"],
            requires_date_table=False
        ))

        # Percentage of Total (Porcentaje del total)
        self.templates.append(DAXTemplate(
            id="percentage_of_total",
            name="Percentage of Total",
            description="Calcula el porcentaje que representa sobre el total",
            category="Calculations",
            difficulty="intermediate",
            parameters=[
                TemplateParameter(
                    name="measure_name",
                    description="Nombre de la nueva medida",
                    type="text",
                    required=True
                ),
                TemplateParameter(
                    name="base_measure",
                    description="Medida base",
                    type="measure",
                    required=True
                )
            ],
            dax_template="""{measure_name} =
DIVIDE(
    [{base_measure}],
    CALCULATE([{base_measure}], ALL())
)""",
            example="""% del Total Ventas =
DIVIDE(
    [Total Ventas],
    CALCULATE([Total Ventas], ALL())
)""",
            tags=["percentage", "total", "porcentaje del total", "all"],
            requires_date_table=False
        ))

        # Margin (Margen)
        self.templates.append(DAXTemplate(
            id="margin",
            name="Margin",
            description="Calcula el margen (Ingresos - Costos)",
            category="Calculations",
            difficulty="basic",
            parameters=[
                TemplateParameter(
                    name="measure_name",
                    description="Nombre de la nueva medida",
                    type="text",
                    required=True
                ),
                TemplateParameter(
                    name="revenue_measure",
                    description="Medida de ingresos",
                    type="measure",
                    required=True
                ),
                TemplateParameter(
                    name="cost_measure",
                    description="Medida de costos",
                    type="measure",
                    required=True
                )
            ],
            dax_template="""{measure_name} = [{revenue_measure}] - [{cost_measure}]""",
            example="""Margen = [Total Ventas] - [Total Costos]""",
            tags=["margin", "margen", "utilidad", "ganancia"],
            requires_date_table=False
        ))

        # Margin Percentage
        self.templates.append(DAXTemplate(
            id="margin_percentage",
            name="Margin Percentage",
            description="Calcula el margen como porcentaje de los ingresos",
            category="Calculations",
            difficulty="basic",
            parameters=[
                TemplateParameter(
                    name="measure_name",
                    description="Nombre de la nueva medida",
                    type="text",
                    required=True
                ),
                TemplateParameter(
                    name="revenue_measure",
                    description="Medida de ingresos",
                    type="measure",
                    required=True
                ),
                TemplateParameter(
                    name="cost_measure",
                    description="Medida de costos",
                    type="measure",
                    required=True
                )
            ],
            dax_template="""{measure_name} =
DIVIDE(
    [{revenue_measure}] - [{cost_measure}],
    [{revenue_measure}]
)""",
            example="""Margen % =
DIVIDE(
    [Total Ventas] - [Total Costos],
    [Total Ventas]
)""",
            tags=["margin", "porcentaje", "profit margin"],
            requires_date_table=False
        ))

        # Variance (Varianza absoluta)
        self.templates.append(DAXTemplate(
            id="variance",
            name="Variance (Absolute)",
            description="Calcula la diferencia absoluta entre dos medidas",
            category="Calculations",
            difficulty="basic",
            parameters=[
                TemplateParameter(
                    name="measure_name",
                    description="Nombre de la nueva medida",
                    type="text",
                    required=True
                ),
                TemplateParameter(
                    name="actual_measure",
                    description="Medida actual/real",
                    type="measure",
                    required=True
                ),
                TemplateParameter(
                    name="target_measure",
                    description="Medida objetivo/presupuesto",
                    type="measure",
                    required=True
                )
            ],
            dax_template="""{measure_name} = [{actual_measure}] - [{target_measure}]""",
            example="""Varianza vs Presupuesto = [Ventas Reales] - [Presupuesto Ventas]""",
            tags=["variance", "varianza", "diferencia", "vs"],
            requires_date_table=False
        ))

        # Variance Percentage
        self.templates.append(DAXTemplate(
            id="variance_percentage",
            name="Variance Percentage",
            description="Calcula la varianza como porcentaje",
            category="Calculations",
            difficulty="basic",
            parameters=[
                TemplateParameter(
                    name="measure_name",
                    description="Nombre de la nueva medida",
                    type="text",
                    required=True
                ),
                TemplateParameter(
                    name="actual_measure",
                    description="Medida actual/real",
                    type="measure",
                    required=True
                ),
                TemplateParameter(
                    name="target_measure",
                    description="Medida objetivo/presupuesto",
                    type="measure",
                    required=True
                )
            ],
            dax_template="""{measure_name} =
DIVIDE(
    [{actual_measure}] - [{target_measure}],
    [{target_measure}]
)""",
            example="""Varianza % =
DIVIDE(
    [Ventas Reales] - [Presupuesto Ventas],
    [Presupuesto Ventas]
)""",
            tags=["variance", "percentage", "varianza porcentual"],
            requires_date_table=False
        ))

        # Growth Rate
        self.templates.append(DAXTemplate(
            id="growth_rate",
            name="Growth Rate",
            description="Calcula la tasa de crecimiento entre dos períodos",
            category="Calculations",
            difficulty="intermediate",
            parameters=[
                TemplateParameter(
                    name="measure_name",
                    description="Nombre de la nueva medida",
                    type="text",
                    required=True
                ),
                TemplateParameter(
                    name="current_measure",
                    description="Medida período actual",
                    type="measure",
                    required=True
                ),
                TemplateParameter(
                    name="previous_measure",
                    description="Medida período anterior",
                    type="measure",
                    required=True
                )
            ],
            dax_template="""{measure_name} =
DIVIDE(
    [{current_measure}] - [{previous_measure}],
    [{previous_measure}]
)""",
            example="""Tasa de Crecimiento =
DIVIDE(
    [Ventas Este Año] - [Ventas Año Pasado],
    [Ventas Año Pasado]
)""",
            tags=["growth", "crecimiento", "tasa", "rate"],
            requires_date_table=False
        ))

        # Index (Base 100)
        self.templates.append(DAXTemplate(
            id="index_base_100",
            name="Index (Base 100)",
            description="Calcula un índice base 100 usando el primer valor como referencia",
            category="Calculations",
            difficulty="advanced",
            parameters=[
                TemplateParameter(
                    name="measure_name",
                    description="Nombre de la nueva medida",
                    type="text",
                    required=True
                ),
                TemplateParameter(
                    name="base_measure",
                    description="Medida base",
                    type="measure",
                    required=True
                ),
                TemplateParameter(
                    name="date_column",
                    description="Columna de fecha",
                    type="date_column",
                    required=True
                )
            ],
            dax_template="""{measure_name} =
VAR FirstValue =
    CALCULATE(
        [{base_measure}],
        FIRSTDATE({date_column})
    )
VAR CurrentValue = [{base_measure}]
RETURN
    DIVIDE(CurrentValue, FirstValue) * 100""",
            example="""Índice Ventas (Base 100) =
VAR FirstValue =
    CALCULATE(
        [Total Ventas],
        FIRSTDATE('Calendario'[Fecha])
    )
VAR CurrentValue = [Total Ventas]
RETURN
    DIVIDE(CurrentValue, FirstValue) * 100""",
            tags=["index", "índice", "base 100", "normalización"],
            requires_date_table=True
        ))

        # Contribution Margin
        self.templates.append(DAXTemplate(
            id="contribution_margin",
            name="Contribution Margin",
            description="Calcula el margen de contribución (Ventas - Costos Variables)",
            category="Calculations",
            difficulty="intermediate",
            parameters=[
                TemplateParameter(
                    name="measure_name",
                    description="Nombre de la nueva medida",
                    type="text",
                    required=True
                ),
                TemplateParameter(
                    name="sales_measure",
                    description="Medida de ventas",
                    type="measure",
                    required=True
                ),
                TemplateParameter(
                    name="variable_cost_measure",
                    description="Medida de costos variables",
                    type="measure",
                    required=True
                )
            ],
            dax_template="""{measure_name} = [{sales_measure}] - [{variable_cost_measure}]""",
            example="""Margen de Contribución = [Ventas] - [Costos Variables]""",
            tags=["contribution", "margen contribución", "margin"],
            requires_date_table=False
        ))

        # Average Ticket/Transaction
        self.templates.append(DAXTemplate(
            id="average_ticket",
            name="Average Ticket",
            description="Calcula el ticket/valor promedio por transacción",
            category="Calculations",
            difficulty="basic",
            parameters=[
                TemplateParameter(
                    name="measure_name",
                    description="Nombre de la nueva medida",
                    type="text",
                    required=True
                ),
                TemplateParameter(
                    name="total_measure",
                    description="Medida de total (ventas, ingresos)",
                    type="measure",
                    required=True
                ),
                TemplateParameter(
                    name="count_measure",
                    description="Medida de conteo (transacciones, tickets)",
                    type="measure",
                    required=True
                )
            ],
            dax_template="""{measure_name} =
DIVIDE(
    [{total_measure}],
    [{count_measure}]
)""",
            example="""Ticket Promedio =
DIVIDE(
    [Total Ventas],
    [Total Transacciones]
)""",
            tags=["average ticket", "ticket promedio", "aov", "average order value"],
            requires_date_table=False
        ))

        # Cumulative Percentage
        self.templates.append(DAXTemplate(
            id="cumulative_percentage",
            name="Cumulative Percentage",
            description="Calcula el porcentaje acumulado (útil para análisis Pareto)",
            category="Calculations",
            difficulty="advanced",
            parameters=[
                TemplateParameter(
                    name="measure_name",
                    description="Nombre de la nueva medida",
                    type="text",
                    required=True
                ),
                TemplateParameter(
                    name="base_measure",
                    description="Medida base",
                    type="measure",
                    required=True
                ),
                TemplateParameter(
                    name="sort_column",
                    description="Columna para ordenar",
                    type="column",
                    required=True
                )
            ],
            dax_template="""{measure_name} =
VAR CurrentTotal =
    CALCULATE(
        [{base_measure}],
        FILTER(
            ALLSELECTED({sort_column}),
            RANKX(
                ALLSELECTED({sort_column}),
                [{base_measure}],
                ,
                DESC
            ) <= RANKX(
                ALLSELECTED({sort_column}),
                [{base_measure}],
                ,
                DESC
            )
        )
    )
VAR GrandTotal =
    CALCULATE(
        [{base_measure}],
        ALLSELECTED()
    )
RETURN
    DIVIDE(CurrentTotal, GrandTotal)""",
            example="""% Acumulado Ventas =
VAR CurrentTotal =
    CALCULATE(
        [Total Ventas],
        FILTER(
            ALLSELECTED(Productos[Nombre]),
            RANKX(
                ALLSELECTED(Productos[Nombre]),
                [Total Ventas],
                ,
                DESC
            ) <= RANKX(
                ALLSELECTED(Productos[Nombre]),
                [Total Ventas],
                ,
                DESC
            )
        )
    )
VAR GrandTotal =
    CALCULATE(
        [Total Ventas],
        ALLSELECTED()
    )
RETURN
    DIVIDE(CurrentTotal, GrandTotal)""",
            tags=["cumulative", "acumulado", "pareto", "running percentage"],
            requires_date_table=False
        ))

        # Conversion Rate
        self.templates.append(DAXTemplate(
            id="conversion_rate",
            name="Conversion Rate",
            description="Calcula la tasa de conversión entre dos eventos/etapas",
            category="Calculations",
            difficulty="basic",
            parameters=[
                TemplateParameter(
                    name="measure_name",
                    description="Nombre de la nueva medida",
                    type="text",
                    required=True
                ),
                TemplateParameter(
                    name="converted_measure",
                    description="Medida de conversiones (ej: ventas)",
                    type="measure",
                    required=True
                ),
                TemplateParameter(
                    name="total_measure",
                    description="Medida de total (ej: visitas)",
                    type="measure",
                    required=True
                )
            ],
            dax_template="""{measure_name} =
DIVIDE(
    [{converted_measure}],
    [{total_measure}]
)""",
            example="""Tasa de Conversión =
DIVIDE(
    [Total Ventas],
    [Total Visitas]
)""",
            tags=["conversion", "conversión", "tasa", "rate"],
            requires_date_table=False
        ))

        # Share of Total (Participación)
        self.templates.append(DAXTemplate(
            id="share_of_total",
            name="Share of Total",
            description="Calcula la participación/share respecto al total de una categoría",
            category="Calculations",
            difficulty="intermediate",
            parameters=[
                TemplateParameter(
                    name="measure_name",
                    description="Nombre de la nueva medida",
                    type="text",
                    required=True
                ),
                TemplateParameter(
                    name="base_measure",
                    description="Medida base",
                    type="measure",
                    required=True
                ),
                TemplateParameter(
                    name="category_column",
                    description="Columna de categoría para ALL",
                    type="column",
                    required=True
                )
            ],
            dax_template="""{measure_name} =
DIVIDE(
    [{base_measure}],
    CALCULATE([{base_measure}], ALL({category_column}))
)""",
            example="""Market Share =
DIVIDE(
    [Total Ventas],
    CALCULATE([Total Ventas], ALL(Productos[Categoría]))
)""",
            tags=["share", "participación", "market share", "porcentaje"],
            requires_date_table=False
        ))
