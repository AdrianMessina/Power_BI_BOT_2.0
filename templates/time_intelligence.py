"""
Templates de Time Intelligence para Power BI
YTD, YoY, MTD, QTD, SPLY, Running Totals, etc.
"""

from typing import List
from .base_template import BaseTemplateCollection, DAXTemplate, TemplateParameter


class TimeIntelligenceTemplates(BaseTemplateCollection):
    """Colección de templates de Time Intelligence"""

    def _load_templates(self):
        """Carga todos los templates de Time Intelligence"""

        # YTD (Year to Date)
        self.templates.append(DAXTemplate(
            id="ytd",
            name="Year to Date (YTD)",
            description="Calcula el acumulado desde el inicio del año hasta la fecha actual",
            category="Time Intelligence",
            difficulty="basic",
            parameters=[
                TemplateParameter(
                    name="measure_name",
                    description="Nombre de la nueva medida",
                    type="text",
                    required=True
                ),
                TemplateParameter(
                    name="base_measure",
                    description="Medida base a acumular",
                    type="measure",
                    required=True
                ),
                TemplateParameter(
                    name="date_column",
                    description="Columna de fecha (ej: 'Calendario'[Fecha])",
                    type="date_column",
                    required=True
                )
            ],
            dax_template="""{measure_name} =
CALCULATE(
    [{base_measure}],
    DATESYTD({date_column})
)""",
            example="""Ventas YTD =
CALCULATE(
    [Total Ventas],
    DATESYTD('Calendario'[Fecha])
)""",
            tags=["ytd", "year to date", "acumulado", "anual"],
            requires_date_table=True
        ))

        # MTD (Month to Date)
        self.templates.append(DAXTemplate(
            id="mtd",
            name="Month to Date (MTD)",
            description="Calcula el acumulado del mes hasta la fecha actual",
            category="Time Intelligence",
            difficulty="basic",
            parameters=[
                TemplateParameter(
                    name="measure_name",
                    description="Nombre de la nueva medida",
                    type="text",
                    required=True
                ),
                TemplateParameter(
                    name="base_measure",
                    description="Medida base a acumular",
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
CALCULATE(
    [{base_measure}],
    DATESMTD({date_column})
)""",
            example="""Ventas MTD =
CALCULATE(
    [Total Ventas],
    DATESMTD('Calendario'[Fecha])
)""",
            tags=["mtd", "month to date", "mensual", "mes"],
            requires_date_table=True
        ))

        # QTD (Quarter to Date)
        self.templates.append(DAXTemplate(
            id="qtd",
            name="Quarter to Date (QTD)",
            description="Calcula el acumulado del trimestre hasta la fecha actual",
            category="Time Intelligence",
            difficulty="basic",
            parameters=[
                TemplateParameter(
                    name="measure_name",
                    description="Nombre de la nueva medida",
                    type="text",
                    required=True
                ),
                TemplateParameter(
                    name="base_measure",
                    description="Medida base a acumular",
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
CALCULATE(
    [{base_measure}],
    DATESQTD({date_column})
)""",
            example="""Ventas QTD =
CALCULATE(
    [Total Ventas],
    DATESQTD('Calendario'[Fecha])
)""",
            tags=["qtd", "quarter to date", "trimestre", "trimestral"],
            requires_date_table=True
        ))

        # Same Period Last Year (SPLY)
        self.templates.append(DAXTemplate(
            id="sply",
            name="Same Period Last Year",
            description="Calcula el valor del mismo período del año anterior",
            category="Time Intelligence",
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
                    name="date_column",
                    description="Columna de fecha",
                    type="date_column",
                    required=True
                )
            ],
            dax_template="""{measure_name} =
CALCULATE(
    [{base_measure}],
    SAMEPERIODLASTYEAR({date_column})
)""",
            example="""Ventas Año Anterior =
CALCULATE(
    [Total Ventas],
    SAMEPERIODLASTYEAR('Calendario'[Fecha])
)""",
            tags=["año anterior", "last year", "py", "comparación"],
            requires_date_table=True
        ))

        # YoY Growth (Year over Year)
        self.templates.append(DAXTemplate(
            id="yoy_growth",
            name="Year over Year Growth",
            description="Calcula el crecimiento porcentual comparado con el año anterior",
            category="Time Intelligence",
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
                    name="date_column",
                    description="Columna de fecha",
                    type="date_column",
                    required=True
                )
            ],
            dax_template="""{measure_name} =
VAR CurrentValue = [{base_measure}]
VAR PreviousYearValue =
    CALCULATE(
        [{base_measure}],
        SAMEPERIODLASTYEAR({date_column})
    )
RETURN
    DIVIDE(
        CurrentValue - PreviousYearValue,
        PreviousYearValue
    )""",
            example="""Crecimiento YoY % =
VAR CurrentValue = [Total Ventas]
VAR PreviousYearValue =
    CALCULATE(
        [Total Ventas],
        SAMEPERIODLASTYEAR('Calendario'[Fecha])
    )
RETURN
    DIVIDE(
        CurrentValue - PreviousYearValue,
        PreviousYearValue
    )""",
            tags=["yoy", "growth", "crecimiento", "variación", "año anterior"],
            requires_date_table=True
        ))

        # Running Total
        self.templates.append(DAXTemplate(
            id="running_total",
            name="Running Total",
            description="Calcula el total acumulado hasta la fecha",
            category="Time Intelligence",
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
                    name="date_column",
                    description="Columna de fecha",
                    type="date_column",
                    required=True
                )
            ],
            dax_template="""{measure_name} =
CALCULATE(
    [{base_measure}],
    FILTER(
        ALL({date_column}),
        {date_column} <= MAX({date_column})
    )
)""",
            example="""Ventas Acumuladas =
CALCULATE(
    [Total Ventas],
    FILTER(
        ALL('Calendario'[Fecha]),
        'Calendario'[Fecha] <= MAX('Calendario'[Fecha])
    )
)""",
            tags=["running total", "acumulado", "cumulative", "total corrido"],
            requires_date_table=True
        ))

        # Moving Average (3 months)
        self.templates.append(DAXTemplate(
            id="moving_avg_3m",
            name="Moving Average (3 Months)",
            description="Calcula el promedio móvil de los últimos 3 meses",
            category="Time Intelligence",
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
CALCULATE(
    AVERAGEX(
        DATESINPERIOD(
            {date_column},
            LASTDATE({date_column}),
            -3,
            MONTH
        ),
        [{base_measure}]
    )
)""",
            example="""Promedio Móvil 3 Meses =
CALCULATE(
    AVERAGEX(
        DATESINPERIOD(
            'Calendario'[Fecha],
            LASTDATE('Calendario'[Fecha]),
            -3,
            MONTH
        ),
        [Total Ventas]
    )
)""",
            tags=["moving average", "promedio móvil", "ma", "tendencia"],
            requires_date_table=True
        ))

        # Last N Days
        self.templates.append(DAXTemplate(
            id="last_n_days",
            name="Last N Days",
            description="Calcula el valor de los últimos N días",
            category="Time Intelligence",
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
                    name="date_column",
                    description="Columna de fecha",
                    type="date_column",
                    required=True
                ),
                TemplateParameter(
                    name="days",
                    description="Número de días (ej: 7, 30, 90)",
                    type="text",
                    required=True
                )
            ],
            dax_template="""{measure_name} =
CALCULATE(
    [{base_measure}],
    DATESINPERIOD(
        {date_column},
        LASTDATE({date_column}),
        -{days},
        DAY
    )
)""",
            example="""Ventas Últimos 30 Días =
CALCULATE(
    [Total Ventas],
    DATESINPERIOD(
        'Calendario'[Fecha],
        LASTDATE('Calendario'[Fecha]),
        -30,
        DAY
    )
)""",
            tags=["last days", "últimos días", "rolling", "período"],
            requires_date_table=True
        ))

        # Prior Month
        self.templates.append(DAXTemplate(
            id="prior_month",
            name="Prior Month",
            description="Calcula el valor del mes anterior",
            category="Time Intelligence",
            difficulty="basic",
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
CALCULATE(
    [{base_measure}],
    DATEADD({date_column}, -1, MONTH)
)""",
            example="""Ventas Mes Anterior =
CALCULATE(
    [Total Ventas],
    DATEADD('Calendario'[Fecha], -1, MONTH)
)""",
            tags=["prior month", "mes anterior", "pm", "comparación"],
            requires_date_table=True
        ))

        # Month over Month Growth
        self.templates.append(DAXTemplate(
            id="mom_growth",
            name="Month over Month Growth",
            description="Calcula el crecimiento porcentual comparado con el mes anterior",
            category="Time Intelligence",
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
                    name="date_column",
                    description="Columna de fecha",
                    type="date_column",
                    required=True
                )
            ],
            dax_template="""{measure_name} =
VAR CurrentValue = [{base_measure}]
VAR PreviousMonthValue =
    CALCULATE(
        [{base_measure}],
        DATEADD({date_column}, -1, MONTH)
    )
RETURN
    DIVIDE(
        CurrentValue - PreviousMonthValue,
        PreviousMonthValue
    )""",
            example="""Crecimiento MoM % =
VAR CurrentValue = [Total Ventas]
VAR PreviousMonthValue =
    CALCULATE(
        [Total Ventas],
        DATEADD('Calendario'[Fecha], -1, MONTH)
    )
RETURN
    DIVIDE(
        CurrentValue - PreviousMonthValue,
        PreviousMonthValue
    )""",
            tags=["mom", "month over month", "crecimiento mensual", "variación"],
            requires_date_table=True
        ))
