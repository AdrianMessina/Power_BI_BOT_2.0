"""
Templates DAX Personalizados para YPF
Medidas específicas del negocio de combustibles y estaciones de servicio
"""

from .base_template import (
    DAXTemplate,
    TemplateParameter,
    BaseTemplateCollection
)


class YPFBusinessTemplates(BaseTemplateCollection):
    """
    Colección de templates para métricas de negocio YPF
    """

    def _load_templates(self):
        """Registra todos los templates de la colección"""

        # 1. Volumen Total de Ventas (Litros)
        self.templates.append(DAXTemplate(
            id='ypf_volumen_total',
            name='Volumen Total de Ventas',
            category='YPF Business',
            description='Suma total de litros vendidos',
            difficulty='basic',
            parameters=[
                TemplateParameter(
                    name='measure_name',
                    type='text',
                    description='Nombre de la medida',
                    required=True
                ),
                TemplateParameter(
                    name='volumen_column',
                    type='column',
                    description='Columna de volumen (litros)',
                    required=True
                )
            ],
            dax_template="{measure_name} = SUM({volumen_column})",
            example="Volumen Total Litros = SUM(Ventas[Litros])",
            tags=['volumen', 'litros', 'ventas', 'combustible']
        ))

        # 2. Precio Promedio por Litro
        self.templates.append(DAXTemplate(
            id='ypf_precio_promedio',
            name='Precio Promedio por Litro',
            category='YPF Business',
            description='Calcula el precio promedio ponderado por litro',
            difficulty='intermediate',
            parameters=[
                TemplateParameter(
                    name='measure_name',
                    type='text',
                    description='Nombre de la medida',
                    required=True
                ),
                TemplateParameter(
                    name='importe_column',
                    type='column',
                    description='Columna de importe total',
                    required=True
                ),
                TemplateParameter(
                    name='volumen_column',
                    type='column',
                    description='Columna de volumen (litros)',
                    required=True
                )
            ],
            dax_template="{measure_name} = DIVIDE(SUM({importe_column}), SUM({volumen_column}), 0)",
            example="Precio Promedio = DIVIDE(SUM(Ventas[Importe]), SUM(Ventas[Litros]), 0)",
            tags=['precio', 'promedio', 'litro', 'ponderado']
        ))

        # 3. Margen de Contribución
        self.templates.append(DAXTemplate(
            id='ypf_margen_contribucion',
            name='Margen de Contribución',
            category='YPF Business',
            description='Calcula margen de contribución (Ventas - Costo Variable)',
            difficulty='intermediate',
            parameters=[
                TemplateParameter(
                    name='measure_name',
                    type='text',
                    description='Nombre de la medida',
                    required=True
                ),
                TemplateParameter(
                    name='ventas_measure',
                    type='measure',
                    description='Medida de ventas totales',
                    required=True
                ),
                TemplateParameter(
                    name='costo_variable_measure',
                    type='measure',
                    description='Medida de costo variable',
                    required=True
                )
            ],
            dax_template="{measure_name} = {ventas_measure} - {costo_variable_measure}",
            example="Margen Contribución = [Total Ventas] - [Costo Variable]",
            tags=['margen', 'contribucion', 'rentabilidad', 'costo']
        ))

        # 4. Margen de Contribución %
        self.templates.append(DAXTemplate(
            id='ypf_margen_contribucion_pct',
            name='Margen de Contribución %',
            category='YPF Business',
            description='Porcentaje de margen de contribución sobre ventas',
            difficulty='intermediate',
            parameters=[
                TemplateParameter(
                    name='measure_name',
                    type='text',
                    description='Nombre de la medida',
                    required=True
                ),
                TemplateParameter(
                    name='margen_measure',
                    type='measure',
                    description='Medida de margen de contribución',
                    required=True
                ),
                TemplateParameter(
                    name='ventas_measure',
                    type='measure',
                    description='Medida de ventas totales',
                    required=True
                )
            ],
            dax_template="{measure_name} = DIVIDE({margen_measure}, {ventas_measure}, 0)",
            example="Margen % = DIVIDE([Margen Contribución], [Total Ventas], 0)",
            tags=['margen', 'porcentaje', 'rentabilidad', 'kpi']
        ))

        # 5. Volumen por Estación
        self.templates.append(DAXTemplate(
            id='ypf_volumen_por_estacion',
            name='Volumen Promedio por Estación',
            category='YPF Business',
            description='Volumen promedio vendido por estación',
            difficulty='intermediate',
            parameters=[
                TemplateParameter(
                    name='measure_name',
                    type='text',
                    description='Nombre de la medida',
                    required=True
                ),
                TemplateParameter(
                    name='volumen_column',
                    type='column',
                    description='Columna de volumen (litros)',
                    required=True
                ),
                TemplateParameter(
                    name='estacion_column',
                    type='column',
                    description='Columna de estación/punto de venta',
                    required=True
                )
            ],
            dax_template="{measure_name} = DIVIDE(SUM({volumen_column}), DISTINCTCOUNT({estacion_column}), 0)",
            example="Volumen x Estación = DIVIDE(SUM(Ventas[Litros]), DISTINCTCOUNT(Ventas[Estacion]), 0)",
            tags=['volumen', 'estacion', 'promedio', 'eficiencia']
        ))

        # 6. Mix de Productos %
        self.templates.append(DAXTemplate(
            id='ypf_mix_productos',
            name='Mix de Productos %',
            category='YPF Business',
            description='Porcentaje de participación de un producto en ventas totales',
            difficulty='intermediate',
            parameters=[
                TemplateParameter(
                    name='measure_name',
                    type='text',
                    description='Nombre de la medida',
                    required=True
                ),
                TemplateParameter(
                    name='ventas_measure',
                    type='measure',
                    description='Medida de ventas',
                    required=True
                )
            ],
            dax_template="""{measure_name} =
DIVIDE(
    {ventas_measure},
    CALCULATE({ventas_measure}, ALL(Productos)),
    0
)""",
            example="""Mix Producto % =
DIVIDE(
    [Total Ventas],
    CALCULATE([Total Ventas], ALL(Productos)),
    0
)""",
            tags=['mix', 'producto', 'participacion', 'porcentaje']
        ))

        # 7. Rotación de Inventario
        self.templates.append(DAXTemplate(
            id='ypf_rotacion_inventario',
            name='Rotación de Inventario',
            category='YPF Business',
            description='Veces que rota el inventario (Ventas / Stock Promedio)',
            difficulty='advanced',
            parameters=[
                TemplateParameter(
                    name='measure_name',
                    type='text',
                    description='Nombre de la medida',
                    required=True
                ),
                TemplateParameter(
                    name='volumen_vendido_measure',
                    type='measure',
                    description='Medida de volumen vendido',
                    required=True
                ),
                TemplateParameter(
                    name='stock_promedio_measure',
                    type='measure',
                    description='Medida de stock promedio',
                    required=True
                )
            ],
            dax_template="{measure_name} = DIVIDE({volumen_vendido_measure}, {stock_promedio_measure}, 0)",
            example="Rotación Inventario = DIVIDE([Volumen Vendido], [Stock Promedio], 0)",
            tags=['inventario', 'rotacion', 'stock', 'eficiencia']
        ))

        # 8. Días de Inventario
        self.templates.append(DAXTemplate(
            id='ypf_dias_inventario',
            name='Días de Inventario',
            category='YPF Business',
            description='Días que dura el inventario actual',
            difficulty='advanced',
            parameters=[
                TemplateParameter(
                    name='measure_name',
                    type='text',
                    description='Nombre de la medida',
                    required=True
                ),
                TemplateParameter(
                    name='stock_actual_measure',
                    type='measure',
                    description='Medida de stock actual',
                    required=True
                ),
                TemplateParameter(
                    name='venta_diaria_measure',
                    type='measure',
                    description='Medida de venta diaria promedio',
                    required=True
                )
            ],
            dax_template="{measure_name} = DIVIDE({stock_actual_measure}, {venta_diaria_measure}, 0)",
            example="Días Inventario = DIVIDE([Stock Actual], [Venta Diaria Promedio], 0)",
            tags=['inventario', 'dias', 'stock', 'cobertura']
        ))

        # 9. Performance de Promoción
        self.templates.append(DAXTemplate(
            id='ypf_performance_promo',
            name='Lift de Promoción %',
            category='YPF Business',
            description='Incremento en ventas durante promoción vs sin promoción',
            difficulty='advanced',
            parameters=[
                TemplateParameter(
                    name='measure_name',
                    type='text',
                    description='Nombre de la medida',
                    required=True
                ),
                TemplateParameter(
                    name='ventas_measure',
                    type='measure',
                    description='Medida de ventas',
                    required=True
                ),
                TemplateParameter(
                    name='promo_column',
                    type='column',
                    description='Columna indicadora de promoción',
                    required=True
                )
            ],
            dax_template="""{measure_name} =
VAR VentasConPromo = CALCULATE({ventas_measure}, {promo_column} = "Si")
VAR VentasSinPromo = CALCULATE({ventas_measure}, {promo_column} = "No")
RETURN
DIVIDE(VentasConPromo - VentasSinPromo, VentasSinPromo, 0)""",
            example="""Lift Promo % =
VAR VentasConPromo = CALCULATE([Total Ventas], Ventas[Promocion] = "Si")
VAR VentasSinPromo = CALCULATE([Total Ventas], Ventas[Promocion] = "No")
RETURN
DIVIDE(VentasConPromo - VentasSinPromo, VentasSinPromo, 0)""",
            tags=['promocion', 'lift', 'performance', 'marketing']
        ))

        # 10. Ticket Promedio
        self.templates.append(DAXTemplate(
            id='ypf_ticket_promedio',
            name='Ticket Promedio',
            category='YPF Business',
            description='Importe promedio por transacción',
            difficulty='basic',
            parameters=[
                TemplateParameter(
                    name='measure_name',
                    type='text',
                    description='Nombre de la medida',
                    required=True
                ),
                TemplateParameter(
                    name='importe_column',
                    type='column',
                    description='Columna de importe',
                    required=True
                ),
                TemplateParameter(
                    name='transaccion_column',
                    type='column',
                    description='Columna de ID de transacción',
                    required=True
                )
            ],
            dax_template="{measure_name} = DIVIDE(SUM({importe_column}), DISTINCTCOUNT({transaccion_column}), 0)",
            example="Ticket Promedio = DIVIDE(SUM(Ventas[Importe]), DISTINCTCOUNT(Ventas[TransaccionID]), 0)",
            tags=['ticket', 'promedio', 'transaccion', 'importe']
        ))

        # 11. Eficiencia Operativa (Ventas por Empleado)
        self.templates.append(DAXTemplate(
            id='ypf_ventas_por_empleado',
            name='Ventas por Empleado',
            category='YPF Business',
            description='Ventas promedio por empleado',
            difficulty='intermediate',
            parameters=[
                TemplateParameter(
                    name='measure_name',
                    type='text',
                    description='Nombre de la medida',
                    required=True
                ),
                TemplateParameter(
                    name='ventas_measure',
                    type='measure',
                    description='Medida de ventas totales',
                    required=True
                ),
                TemplateParameter(
                    name='empleado_column',
                    type='column',
                    description='Columna de empleado/personal',
                    required=True
                )
            ],
            dax_template="{measure_name} = DIVIDE({ventas_measure}, DISTINCTCOUNT({empleado_column}), 0)",
            example="Ventas x Empleado = DIVIDE([Total Ventas], DISTINCTCOUNT(Personal[EmpleadoID]), 0)",
            tags=['eficiencia', 'empleado', 'productividad', 'operativa']
        ))

        # 12. Penetración de Producto
        self.templates.append(DAXTemplate(
            id='ypf_penetracion_producto',
            name='Penetración de Producto %',
            category='YPF Business',
            description='% de estaciones que venden un producto específico',
            difficulty='intermediate',
            parameters=[
                TemplateParameter(
                    name='measure_name',
                    type='text',
                    description='Nombre de la medida',
                    required=True
                ),
                TemplateParameter(
                    name='estacion_column',
                    type='column',
                    description='Columna de estación',
                    required=True
                )
            ],
            dax_template="""{measure_name} =
VAR EstacionesConProducto = DISTINCTCOUNT({estacion_column})
VAR TotalEstaciones = CALCULATE(DISTINCTCOUNT({estacion_column}), ALL(Productos))
RETURN
DIVIDE(EstacionesConProducto, TotalEstaciones, 0)""",
            example="""Penetración % =
VAR EstacionesConProducto = DISTINCTCOUNT(Ventas[Estacion])
VAR TotalEstaciones = CALCULATE(DISTINCTCOUNT(Ventas[Estacion]), ALL(Productos))
RETURN
DIVIDE(EstacionesConProducto, TotalEstaciones, 0)""",
            tags=['penetracion', 'producto', 'cobertura', 'distribucion']
        ))

        # 13. Comparativa vs Budget
        self.templates.append(DAXTemplate(
            id='ypf_vs_budget',
            name='Real vs Budget',
            category='YPF Business',
            description='Comparación de ventas reales contra presupuesto',
            difficulty='intermediate',
            parameters=[
                TemplateParameter(
                    name='measure_name',
                    type='text',
                    description='Nombre de la medida',
                    required=True
                ),
                TemplateParameter(
                    name='real_measure',
                    type='measure',
                    description='Medida de valor real',
                    required=True
                ),
                TemplateParameter(
                    name='budget_measure',
                    type='measure',
                    description='Medida de presupuesto',
                    required=True
                )
            ],
            dax_template="{measure_name} = {real_measure} - {budget_measure}",
            example="Diferencia vs Budget = [Ventas Reales] - [Ventas Budget]",
            tags=['budget', 'presupuesto', 'comparacion', 'varianza']
        ))

        # 14. % Cumplimiento Budget
        self.templates.append(DAXTemplate(
            id='ypf_cumplimiento_budget',
            name='% Cumplimiento Budget',
            category='YPF Business',
            description='Porcentaje de cumplimiento del presupuesto',
            difficulty='intermediate',
            parameters=[
                TemplateParameter(
                    name='measure_name',
                    type='text',
                    description='Nombre de la medida',
                    required=True
                ),
                TemplateParameter(
                    name='real_measure',
                    type='measure',
                    description='Medida de valor real',
                    required=True
                ),
                TemplateParameter(
                    name='budget_measure',
                    type='measure',
                    description='Medida de presupuesto',
                    required=True
                )
            ],
            dax_template="{measure_name} = DIVIDE({real_measure}, {budget_measure}, 0)",
            example="% Cumplimiento = DIVIDE([Ventas Reales], [Ventas Budget], 0)",
            tags=['budget', 'cumplimiento', 'porcentaje', 'kpi']
        ))

        # 15. Top N Estaciones por Volumen
        self.templates.append(DAXTemplate(
            id='ypf_top_estaciones',
            name='Top N Estaciones',
            category='YPF Business',
            description='Filtro para mostrar solo las top N estaciones por volumen',
            difficulty='advanced',
            parameters=[
                TemplateParameter(
                    name='measure_name',
                    type='text',
                    description='Nombre de la medida',
                    required=True
                ),
                TemplateParameter(
                    name='volumen_measure',
                    type='measure',
                    description='Medida de volumen',
                    required=True
                ),
                TemplateParameter(
                    name='estacion_column',
                    type='column',
                    description='Columna de estación',
                    required=True
                ),
                TemplateParameter(
                    name='top_n',
                    type='text',
                    description='Número de top estaciones (ej: 10)',
                    required=True
                )
            ],
            dax_template="""{measure_name} =
IF(
    RANKX(
        ALL({estacion_column}),
        {volumen_measure},
        ,
        DESC,
        DENSE
    ) <= {top_n},
    {volumen_measure},
    BLANK()
)""",
            example="""Top 10 Estaciones =
IF(
    RANKX(
        ALL(Ventas[Estacion]),
        [Volumen Total],
        ,
        DESC,
        DENSE
    ) <= 10,
    [Volumen Total],
    BLANK()
)""",
            tags=['top', 'ranking', 'estaciones', 'filtro'],
            requires_date_table=False
        ))


# Exportar para usar en template_manager
__all__ = ['YPFBusinessTemplates']
