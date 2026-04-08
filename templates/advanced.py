"""
Templates Avanzados para Power BI
Ranking, ABC Analysis, Pareto, Top N, Dynamic calculations
"""

from typing import List
from .base_template import BaseTemplateCollection, DAXTemplate, TemplateParameter


class AdvancedTemplates(BaseTemplateCollection):
    """Colección de templates avanzados"""

    def _load_templates(self):
        """Carga todos los templates avanzados"""

        # RANKX - Ranking
        self.templates.append(DAXTemplate(
            id="rank",
            name="Rank",
            description="Asigna un ranking basado en una medida",
            category="Advanced",
            difficulty="intermediate",
            parameters=[
                TemplateParameter(
                    name="measure_name",
                    description="Nombre de la nueva medida",
                    type="text",
                    required=True
                ),
                TemplateParameter(
                    name="ranking_measure",
                    description="Medida a rankear",
                    type="measure",
                    required=True
                ),
                TemplateParameter(
                    name="ranking_column",
                    description="Columna sobre la que rankear",
                    type="column",
                    required=True
                )
            ],
            dax_template="""{measure_name} =
RANKX(
    ALL({ranking_column}),
    [{ranking_measure}],
    ,
    DESC
)""",
            example="""Ranking Productos =
RANKX(
    ALL(Productos[Nombre]),
    [Total Ventas],
    ,
    DESC
)""",
            tags=["rank", "ranking", "rankx", "position"],
            requires_date_table=False
        ))

        # Top N
        self.templates.append(DAXTemplate(
            id="top_n",
            name="Top N",
            description="Muestra solo los Top N elementos por una medida",
            category="Advanced",
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
                    name="top_n",
                    description="Número de elementos (ej: 10)",
                    type="text",
                    required=True
                ),
                TemplateParameter(
                    name="ranking_column",
                    description="Columna sobre la que rankear",
                    type="column",
                    required=True
                )
            ],
            dax_template="""{measure_name} =
IF(
    RANKX(
        ALL({ranking_column}),
        [{base_measure}],
        ,
        DESC
    ) <= {top_n},
    [{base_measure}],
    BLANK()
)""",
            example="""Top 10 Ventas =
IF(
    RANKX(
        ALL(Productos[Nombre]),
        [Total Ventas],
        ,
        DESC
    ) <= 10,
    [Total Ventas],
    BLANK()
)""",
            tags=["top n", "top 10", "filter", "ranking"],
            requires_date_table=False
        ))

        # ABC Classification
        self.templates.append(DAXTemplate(
            id="abc_classification",
            name="ABC Classification",
            description="Clasifica elementos en categorías A (top 80%), B (siguiente 15%), C (último 5%)",
            category="Advanced",
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
                    description="Medida base para clasificar",
                    type="measure",
                    required=True
                ),
                TemplateParameter(
                    name="item_column",
                    description="Columna de items a clasificar",
                    type="column",
                    required=True
                )
            ],
            dax_template="""{measure_name} =
VAR CurrentTotal =
    CALCULATE(
        [{base_measure}],
        FILTER(
            ALLSELECTED({item_column}),
            RANKX(
                ALLSELECTED({item_column}),
                [{base_measure}],
                ,
                DESC
            ) <= RANKX(
                ALLSELECTED({item_column}),
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
VAR CumulativePercentage = DIVIDE(CurrentTotal, GrandTotal)
RETURN
    SWITCH(
        TRUE(),
        CumulativePercentage <= 0.80, "A",
        CumulativePercentage <= 0.95, "B",
        "C"
    )""",
            example="""Clasificación ABC Productos =
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
VAR CumulativePercentage = DIVIDE(CurrentTotal, GrandTotal)
RETURN
    SWITCH(
        TRUE(),
        CumulativePercentage <= 0.80, "A",
        CumulativePercentage <= 0.95, "B",
        "C"
    )""",
            tags=["abc", "classification", "clasificación", "pareto"],
            requires_date_table=False
        ))

        # Pareto 80/20
        self.templates.append(DAXTemplate(
            id="pareto_80_20",
            name="Pareto 80/20",
            description="Identifica si un elemento está en el Top 80% (Pareto)",
            category="Advanced",
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
                    name="item_column",
                    description="Columna de items",
                    type="column",
                    required=True
                )
            ],
            dax_template="""{measure_name} =
VAR CurrentTotal =
    CALCULATE(
        [{base_measure}],
        FILTER(
            ALLSELECTED({item_column}),
            RANKX(
                ALLSELECTED({item_column}),
                [{base_measure}],
                ,
                DESC
            ) <= RANKX(
                ALLSELECTED({item_column}),
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
VAR CumulativePercentage = DIVIDE(CurrentTotal, GrandTotal)
RETURN
    IF(CumulativePercentage <= 0.80, "Top 80%", "Bottom 20%")""",
            example="""Pareto Clientes =
VAR CurrentTotal =
    CALCULATE(
        [Total Ventas],
        FILTER(
            ALLSELECTED(Clientes[Nombre]),
            RANKX(
                ALLSELECTED(Clientes[Nombre]),
                [Total Ventas],
                ,
                DESC
            ) <= RANKX(
                ALLSELECTED(Clientes[Nombre]),
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
VAR CumulativePercentage = DIVIDE(CurrentTotal, GrandTotal)
RETURN
    IF(CumulativePercentage <= 0.80, "Top 80%", "Bottom 20%")""",
            tags=["pareto", "80/20", "vital few", "trivial many"],
            requires_date_table=False
        ))

        # Dynamic Top N (con parámetro)
        self.templates.append(DAXTemplate(
            id="dynamic_top_n",
            name="Dynamic Top N (with Parameter)",
            description="Top N dinámico controlado por parámetro/slicer",
            category="Advanced",
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
                    name="parameter_table",
                    description="Tabla de parámetro (ej: TopN)",
                    type="table",
                    required=True
                ),
                TemplateParameter(
                    name="parameter_column",
                    description="Columna del parámetro (ej: TopN[Value])",
                    type="column",
                    required=True
                ),
                TemplateParameter(
                    name="ranking_column",
                    description="Columna sobre la que rankear",
                    type="column",
                    required=True
                )
            ],
            dax_template="""{measure_name} =
VAR SelectedN = SELECTEDVALUE({parameter_column}, 10)
VAR Ranking =
    RANKX(
        ALL({ranking_column}),
        [{base_measure}],
        ,
        DESC
    )
RETURN
    IF(
        Ranking <= SelectedN,
        [{base_measure}],
        BLANK()
    )""",
            example="""Top N Dinámico =
VAR SelectedN = SELECTEDVALUE(TopN[Value], 10)
VAR Ranking =
    RANKX(
        ALL(Productos[Nombre]),
        [Total Ventas],
        ,
        DESC
    )
RETURN
    IF(
        Ranking <= SelectedN,
        [Total Ventas],
        BLANK()
    )""",
            tags=["dynamic", "parameter", "top n", "slicer"],
            requires_date_table=False
        ))

        # Running Rank
        self.templates.append(DAXTemplate(
            id="running_rank",
            name="Running Rank",
            description="Ranking acumulado por fecha",
            category="Advanced",
            difficulty="advanced",
            parameters=[
                TemplateParameter(
                    name="measure_name",
                    description="Nombre de la nueva medida",
                    type="text",
                    required=True
                ),
                TemplateParameter(
                    name="ranking_measure",
                    description="Medida a rankear",
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
                    name="item_column",
                    description="Columna de items",
                    type="column",
                    required=True
                )
            ],
            dax_template="""{measure_name} =
RANKX(
    FILTER(
        ALL({item_column}),
        CALCULATE([{ranking_measure}]) > 0
    ),
    CALCULATE(
        [{ranking_measure}],
        FILTER(
            ALL({date_column}),
            {date_column} <= MAX({date_column})
        )
    ),
    ,
    DESC
)""",
            example="""Ranking Acumulado Productos =
RANKX(
    FILTER(
        ALL(Productos[Nombre]),
        CALCULATE([Total Ventas]) > 0
    ),
    CALCULATE(
        [Total Ventas],
        FILTER(
            ALL('Calendario'[Fecha]),
            'Calendario'[Fecha] <= MAX('Calendario'[Fecha])
        )
    ),
    ,
    DESC
)""",
            tags=["running rank", "ranking acumulado", "time-based"],
            requires_date_table=True
        ))

        # First/Last Date with Value
        self.templates.append(DAXTemplate(
            id="first_date_with_value",
            name="First Date with Value",
            description="Encuentra la primera fecha en que ocurre un valor/evento",
            category="Advanced",
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
                    description="Medida a evaluar",
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
    MIN({date_column}),
    FILTER(
        ALL({date_column}),
        [{base_measure}] > 0
    )
)""",
            example="""Primera Venta =
CALCULATE(
    MIN('Calendario'[Fecha]),
    FILTER(
        ALL('Calendario'[Fecha]),
        [Total Ventas] > 0
    )
)""",
            tags=["first date", "primera fecha", "min date", "occurrence"],
            requires_date_table=True
        ))

        # Days Since Last Event
        self.templates.append(DAXTemplate(
            id="days_since_last",
            name="Days Since Last Event",
            description="Calcula días transcurridos desde último evento/valor",
            category="Advanced",
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
                    description="Medida a evaluar",
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
VAR LastDate =
    CALCULATE(
        MAX({date_column}),
        FILTER(
            ALL({date_column}),
            [{base_measure}] > 0
        )
    )
VAR CurrentDate = MAX({date_column})
RETURN
    DATEDIFF(LastDate, CurrentDate, DAY)""",
            example="""Días Desde Última Venta =
VAR LastDate =
    CALCULATE(
        MAX('Calendario'[Fecha]),
        FILTER(
            ALL('Calendario'[Fecha]),
            [Total Ventas] > 0
        )
    )
VAR CurrentDate = MAX('Calendario'[Fecha])
RETURN
    DATEDIFF(LastDate, CurrentDate, DAY)""",
            tags=["days since", "días desde", "recency", "last event"],
            requires_date_table=True
        ))

        # Conditional Formatting Helper
        self.templates.append(DAXTemplate(
            id="conditional_format_helper",
            name="Conditional Formatting Helper",
            description="Retorna valores para formateo condicional (Semáforo)",
            category="Advanced",
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
                    description="Medida a evaluar",
                    type="measure",
                    required=True
                ),
                TemplateParameter(
                    name="good_threshold",
                    description="Umbral bueno (ej: 0.1 para 10%)",
                    type="text",
                    required=True
                ),
                TemplateParameter(
                    name="bad_threshold",
                    description="Umbral malo (ej: -0.05 para -5%)",
                    type="text",
                    required=True
                )
            ],
            dax_template="""{measure_name} =
SWITCH(
    TRUE(),
    [{base_measure}] >= {good_threshold}, "Green",
    [{base_measure}] <= {bad_threshold}, "Red",
    "Yellow"
)""",
            example="""Semáforo Ventas =
SWITCH(
    TRUE(),
    [Crecimiento YoY] >= 0.1, "Green",
    [Crecimiento YoY] <= -0.05, "Red",
    "Yellow"
)""",
            tags=["conditional formatting", "traffic light", "semáforo", "kpi"],
            requires_date_table=False
        ))

        # SWITCH - Multiple Conditions
        self.templates.append(DAXTemplate(
            id="switch_categorization",
            name="Switch Categorization",
            description="Categoriza valores en grupos usando SWITCH",
            category="Advanced",
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
                    description="Medida a categorizar",
                    type="measure",
                    required=True
                ),
                TemplateParameter(
                    name="threshold_1",
                    description="Umbral 1 (ej: 1000)",
                    type="text",
                    required=True
                ),
                TemplateParameter(
                    name="threshold_2",
                    description="Umbral 2 (ej: 5000)",
                    type="text",
                    required=True
                )
            ],
            dax_template="""{measure_name} =
SWITCH(
    TRUE(),
    [{base_measure}] < {threshold_1}, "Low",
    [{base_measure}] < {threshold_2}, "Medium",
    "High"
)""",
            example="""Categoría Cliente =
SWITCH(
    TRUE(),
    [Total Ventas] < 1000, "Low",
    [Total Ventas] < 5000, "Medium",
    "High"
)""",
            tags=["switch", "categorization", "classification", "buckets"],
            requires_date_table=False
        ))
