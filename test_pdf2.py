import json
import matplotlib.pyplot as plt
import networkx as nx
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, ListFlowable, ListItem
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import PageBreak
import os

# -----------------------------
# 1️⃣ LOAD YOUR JSON DATA
# -----------------------------

data = { "requirements": { "project_name": "Plataforma IoT Industrial", "domain": "Industria", "stakeholders": [ "{'rol': 'Equipo de Operaciones', 'requerimientos': [{'id': 1, 'title': 'Alertas claras y accionables', 'description': 'Requerimos alertas claras y accionables para tomar decisiones en tiempo real', 'priority': 'high', 'rationale': 'La falta de alertas claras y accionables puede llevar a retrasos en la producci\u00f3n y afectar la calidad del producto'}]}", "{'rol': 'Equipo de Mantenimiento', 'requerimientos': [{'id': 2, 'title': 'Diagn\u00f3sticos predictivos', 'description': 'Requerimos diagn\u00f3sticos predictivos para anticipar fallas y evitar retrasos en la producci\u00f3n', 'priority': 'high', 'rationale': 'La falta de diagn\u00f3sticos predictivos puede llevar a retrasos en la producci\u00f3n y afectar la calidad del producto'}]}", "{'rol': '\u00c1rea de Log\u00edstica', 'requerimientos': [{'id': 3, 'title': 'Monitoreo en tiempo real', 'description': 'Requerimos monitoreo en tiempo real del estado de equipos en centros de distribuci\u00f3n', 'priority': 'medium', 'rationale': 'La falta de monitoreo en tiempo real puede llevar a retrasos en la entrega de productos y afectar la calidad del servicio'}]}", "{'rol': 'Direcci\u00f3n Ejecutiva', 'requerimientos': [{'id': 4, 'title': 'M\u00e9tricas consolidadas', 'description': 'Requerimos m\u00e9tricas consolidadas y comparables entre sedes', 'priority': 'high', 'rationale': 'La falta de m\u00e9tricas consolidadas y comparables puede llevar a decisiones informadas y afectar la toma de decisiones estrat\u00e9gicas'}]}", "{'rol': 'Equipo de TI', 'requerimientos': [{'id': 5, 'title': 'Integraci\u00f3n con sistemas existentes', 'description': 'Requerimos integraci\u00f3n con sistemas existentes sin comprometer seguridad ni estabilidad', 'priority': 'high', 'rationale': 'La falta de integraci\u00f3n con sistemas existentes puede llevar a retrasos en la implementaci\u00f3n y afectar la seguridad y estabilidad de la plataforma'}]}" ], "business_goals": [ "{'id': 1, 'title': 'Reducci\u00f3n de fallas no planificadas', 'description': 'Reducir la frecuencia de fallas no planificadas en la producci\u00f3n', 'priority': 'high', 'rationale': 'La reducci\u00f3n de fallas no planificadas puede llevar a una mayor eficiencia en la producci\u00f3n y afectar la calidad del producto'}", "{'id': 2, 'title': 'Disminuci\u00f3n del consumo energ\u00e9tico', 'description': 'Disminuir el consumo energ\u00e9tico en la producci\u00f3n', 'priority': 'medium', 'rationale': 'La disminuci\u00f3n del consumo energ\u00e9tico puede llevar a una mayor eficiencia en la producci\u00f3n y afectar la calidad del producto'}", "{'id': 3, 'title': 'Reducci\u00f3n del tiempo medio de reparaci\u00f3n', 'description': 'Reducir el tiempo medio de reparaci\u00f3n de equipos cr\u00edticos', 'priority': 'high', 'rationale': 'La reducci\u00f3n del tiempo medio de reparaci\u00f3n puede llevar a una mayor eficiencia en la producci\u00f3n y afectar la calidad del producto'}", "{'id': 4, 'title': 'Aumento en la disponibilidad de activos cr\u00edticos', 'description': 'Aumentar la disponibilidad de activos cr\u00edticos en la producci\u00f3n', 'priority': 'high', 'rationale': 'La disponibilidad de activos cr\u00edticos puede afectar la calidad del producto y la eficiencia en la producci\u00f3n'}" ], "functional_requirements": [ { "id": "1", "title": "Sensores y dispositivos edge", "description": "Requerimos sensores y dispositivos edge para capturar variables cr\u00edticas en tiempo real", "priority": "high", "rationale": "La falta de sensores y dispositivos edge puede llevar a una falta de visibilidad en tiempo real y afectar la toma de decisiones" }, { "id": "2", "title": "Plataforma de IoT industrial", "description": "Requerimos una plataforma de IoT industrial para conectar activos f\u00edsicos con una capa digital", "priority": "high", "rationale": "La falta de una plataforma de IoT industrial puede llevar a una falta de integraci\u00f3n entre activos f\u00edsicos y sistemas digitales" }, { "id": "3", "title": "Modelos predictivos", "description": "Requerimos modelos predictivos para anticipar fallas y optimizar mantenimiento", "priority": "high", "rationale": "La falta de modelos predictivos puede llevar a una falta de anticipaci\u00f3n de fallas y afectar la eficiencia en la producci\u00f3n" } ], "non_functional_requirements": [ { "id": "1", "category": "Seguridad", "requirement": "Garantizar la seguridad de la plataforma", "measurable_target": "99,99%" }, { "id": "2", "category": "Estabilidad", "requirement": "Garantizar la estabilidad de la plataforma", "measurable_target": "99,99%" }, { "id": "3", "category": "Escalabilidad", "requirement": "Garantizar la escalabilidad de la plataforma", "measurable_target": "100%" }, { "id": "4", "category": "Interoperabilidad", "requirement": "Garantizar la interoperabilidad de la plataforma", "measurable_target": "100%" } ], "constraints": [ "{'id': 1, 'description': 'Operamos en un entorno regulado en materia de seguridad industrial y protecci\u00f3n de datos', 'priority': 'high'}", "{'id': 2, 'description': 'Debemos garantizar ciberseguridad de nivel industrial', 'priority': 'high'}", "{'id': 3, 'description': 'La soluci\u00f3n debe ser escalable y modular', 'priority': 'high'}", "{'id': 4, 'description': 'El presupuesto es significativo, pero no ilimitado', 'priority': 'high'}" ], "assumptions": [ "{'id': 1, 'description': 'La plataforma de IoT industrial ser\u00e1 implementada en todas las sedes', 'priority': 'high'}", "{'id': 2, 'description': 'La plataforma de IoT industrial ser\u00e1 integrada con sistemas existentes', 'priority': 'high'}", "{'id': 3, 'description': 'La plataforma de IoT industrial ser\u00e1 escalable y modular', 'priority': 'high'}" ], "open_questions": [ "functional_requirements: [{'id': 1, 'title': '\u00bfC\u00f3mo se integrar\u00e1 la plataforma de IoT industrial con sistemas existentes?', 'description': 'Requerimos una descripci\u00f3n detallada de c\u00f3mo se integrar\u00e1 la plataforma de IoT industrial con sistemas existentes', 'priority': 'high'}, {'id': 2, 'title': '\u00bfC\u00f3mo se garantizar\u00e1 la seguridad de la plataforma?', 'description': 'Requerimos una descripci\u00f3n detallada de c\u00f3mo se garantizar\u00e1 la seguridad de la plataforma', 'priority': 'high'}, {'id': 3, 'title': '\u00bfC\u00f3mo se medir\u00e1 el \u00e9xito de la implementaci\u00f3n de la plataforma de IoT industrial?', 'description': 'Requerimos una descripci\u00f3n detallada de c\u00f3mo se medir\u00e1 el \u00e9xito de la implementaci\u00f3n de la plataforma de IoT industrial', 'priority': 'high'}]" ] }, "inception": { "product_summary": "Una soluci\u00f3n IoT industrial robusta, escalable e inteligente que conecte nuestros activos f\u00edsicos con una capa digital capaz de generar valor tangible.", "problem_statement": "La falta de visibilidad unificada y en tiempo real del estado de nuestros activos f\u00edsicos, la complejidad de integraci\u00f3n con sistemas heredados, la resistencia cultural del personal operativo y la posibilidad de generar una sobrecarga de datos sin capacidad real de an\u00e1lisis.", "value_proposition": "Una plataforma de IoT industrial que conecte nuestros activos f\u00edsicos con una capa digital capaz de generar valor tangible, reducir la complejidad de integraci\u00f3n con sistemas heredados, mejorar la visibilidad en tiempo real del estado de nuestros activos f\u00edsicos y aumentar la disponibilidad de activos cr\u00edticos.", "mvp_in_scope": [ "description: Un piloto en dos plantas representativas: una altamente automatizada y otra con infraestructura m\u00e1s antigua.", "features: ['Sensores y dispositivos edge', 'Plataforma de IoT industrial', 'Modelos predictivos']" ], "mvp_out_of_scope": [ "description: La implementaci\u00f3n en todas las sedes, la integraci\u00f3n con sistemas existentes y la escalabilidad y modularidad de la plataforma.", "features: ['Implementaci\u00f3n en todas las sedes', 'Integraci\u00f3n con sistemas existentes', 'Escalabilidad y modularidad']" ], "risks": [ { "id": "1", "description": "La complejidad de integraci\u00f3n con sistemas heredados", "impact": "high", "probability": "high", "mitigation": "Desarrollar un plan de integraci\u00f3n detallado y realizar pruebas exhaustivas antes de la implementaci\u00f3n." }, { "id": "2", "description": "La resistencia cultural del personal operativo", "impact": "medium", "probability": "medium", "mitigation": "Realizar sesiones de capacitaci\u00f3n y concientizaci\u00f3n para el personal operativo sobre los beneficios de la plataforma de IoT industrial." }, { "id": "3", "description": "La posibilidad de generar una sobrecarga de datos sin capacidad real de an\u00e1lisis", "impact": "high", "probability": "high", "mitigation": "Desarrollar un plan de an\u00e1lisis de datos detallado y realizar pruebas exhaustivas antes de la implementaci\u00f3n." } ], "success_metrics": [ "{'id': 1, 'description': 'Reducci\u00f3n porcentual de fallas no planificadas', 'target': '20%', 'unit': '%'}", "{'id': 2, 'description': 'Disminuci\u00f3n del consumo energ\u00e9tico por unidad producida', 'target': '15%', 'unit': '%'}", "{'id': 3, 'description': 'Reducci\u00f3n del tiempo medio de reparaci\u00f3n', 'target': '30%', 'unit': '%'}", "{'id': 4, 'description': 'Aumento en la disponibilidad de activos cr\u00edticos', 'target': '25%', 'unit': '%'}" ], "release_strategy": "Un plan de lanzamiento gradual y escalable que permita la implementaci\u00f3n de la plataforma de IoT industrial en todas las sedes." }, "user_stories": { "epics": [ "{'id': 1, 'title': 'Plataforma IoT Industrial', 'description': 'Una soluci\u00f3n IoT industrial robusta, escalable e inteligente que conecte nuestros activos f\u00edsicos con una capa digital capaz de generar valor tangible.', 'user_stories': [{'id': 1, 'title': 'Sensores y dispositivos edge', 'description': 'Requerimos sensores y dispositivos edge para capturar variables cr\u00edticas en tiempo real', 'priority': 'high', 'acceptance_criteria': ['Los sensores y dispositivos edge deben ser capaces de capturar variables cr\u00edticas en tiempo real', 'Los sensores y dispositivos edge deben ser compatibles con la plataforma de IoT industrial', 'Los sensores y dispositivos edge deben ser escalables y modulares']}, {'id': 2, 'title': 'Plataforma de IoT industrial', 'description': 'Requerimos una plataforma de IoT industrial para conectar activos f\u00edsicos con una capa digital', 'priority': 'high', 'acceptance_criteria': ['La plataforma de IoT industrial debe ser capaz de conectar activos f\u00edsicos con una capa digital', 'La plataforma de IoT industrial debe ser compatible con sensores y dispositivos edge', 'La plataforma de IoT industrial debe ser escalable y modular']}, {'id': 3, 'title': 'Modelos predictivos', 'description': 'Requerimos modelos predictivos para anticipar fallas y optimizar mantenimiento', 'priority': 'high', 'acceptance_criteria': ['Los modelos predictivos deben ser capaces de anticipar fallas y optimizar mantenimiento', 'Los modelos predictivos deben ser compatibles con la plataforma de IoT industrial', 'Los modelos predictivos deben ser escalables y modulares']}]}" ], "user_stories": [], "dependencies": [ "{'id': 1, 'title': 'Sensores y dispositivos edge', 'description': 'Los sensores y dispositivos edge deben ser capaces de capturar variables cr\u00edticas en tiempo real', 'priority': 'high', 'acceptance_criteria': ['Los sensores y dispositivos edge deben ser capaces de capturar variables cr\u00edticas en tiempo real', 'Los sensores y dispositivos edge deben ser compatibles con la plataforma de IoT industrial', 'Los sensores y dispositivos edge deben ser escalables y modulares']}", "{'id': 2, 'title': 'Plataforma de IoT industrial', 'description': 'La plataforma de IoT industrial debe ser capaz de conectar activos f\u00edsicos con una capa digital', 'priority': 'high', 'acceptance_criteria': ['La plataforma de IoT industrial debe ser capaz de conectar activos f\u00edsicos con una capa digital', 'La plataforma de IoT industrial debe ser compatible con sensores y dispositivos edge', 'La plataforma de IoT industrial debe ser escalable y modular']}", "{'id': 3, 'title': 'Modelos predictivos', 'description': 'Los modelos predictivos deben ser capaces de anticipar fallas y optimizar mantenimiento', 'priority': 'high', 'acceptance_criteria': ['Los modelos predictivos deben ser capaces de anticipar fallas y optimizar mantenimiento', 'Los modelos predictivos deben ser compatibles con la plataforma de IoT industrial', 'Los modelos predictivos deben ser escalables y modulares']}" ] }, "er_design": { "entities": [ { "name": "Plataforma IoT Industrial", "description": "Una soluci\u00f3n IoT industrial robusta, escalable e inteligente que conecte nuestros activos f\u00edsicos con una capa digital capaz de generar valor tangible.", "attributes": [ { "name": "id", "data_type": "string", "is_primary_key": True, "is_foreign_key": False, "nullable": False, "unique": True, "description": "Identificador unico de la plataforma" }, { "name": "nombre", "data_type": "string", "is_primary_key": False, "is_foreign_key": False, "nullable": False, "unique": False, "description": "Nombre de la plataforma" }, { "name": "descripcion", "data_type": "string", "is_primary_key": False, "is_foreign_key": False, "nullable": False, "unique": False, "description": "Descripci\u00f3n de la plataforma" }, { "name": "estado", "data_type": "string", "is_primary_key": False, "is_foreign_key": False, "nullable": False, "unique": False, "description": "Estado de la plataforma" } ], "relationships": [ { "to_entity": "Sensores y dispositivos edge", "cardinality": "1:N", "description": "Relaci\u00f3n entre la plataforma y los sensores y dispositivos edge", "foreign_key": "id_plataforma" }, { "to_entity": "Modelos predictivos", "cardinality": "1:N", "description": "Relaci\u00f3n entre la plataforma y los modelos predictivos", "foreign_key": "id_plataforma" } ] }, { "name": "Sensores y dispositivos edge", "description": "Sensores y dispositivos edge para capturar variables cr\u00edticas en tiempo real", "attributes": [ { "name": "id", "data_type": "string", "is_primary_key": True, "is_foreign_key": False, "nullable": False, "unique": True, "description": "Identificador unico de los sensores y dispositivos edge" }, { "name": "nombre", "data_type": "string", "is_primary_key": False, "is_foreign_key": False, "nullable": False, "unique": False, "description": "Nombre de los sensores y dispositivos edge" }, { "name": "descripcion", "data_type": "string", "is_primary_key": False, "is_foreign_key": False, "nullable": False, "unique": False, "description": "Descripci\u00f3n de los sensores y dispositivos edge" }, { "name": "estado", "data_type": "string", "is_primary_key": False, "is_foreign_key": False, "nullable": False, "unique": False, "description": "Estado de los sensores y dispositivos edge" } ], "relationships": [ { "to_entity": "Plataforma IoT Industrial", "cardinality": "1:N", "description": "Relaci\u00f3n entre los sensores y dispositivos edge y la plataforma", "foreign_key": "id_plataforma" } ] }, { "name": "Modelos predictivos", "description": "Modelos predictivos para anticipar fallas y optimizar mantenimiento", "attributes": [ { "name": "id", "data_type": "string", "is_primary_key": True, "is_foreign_key": False, "nullable": False, "unique": True, "description": "Identificador unico de los modelos predictivos" }, { "name": "nombre", "data_type": "string", "is_primary_key": False, "is_foreign_key": False, "nullable": False, "unique": False, "description": "Nombre de los modelos predictivos" }, { "name": "descripcion", "data_type": "string", "is_primary_key": False, "is_foreign_key": False, "nullable": False, "unique": False, "description": "Descripci\u00f3n de los modelos predictivos" }, { "name": "estado", "data_type": "string", "is_primary_key": False, "is_foreign_key": False, "nullable": False, "unique": False, "description": "Estado de los modelos predictivos" } ], "relationships": [ { "to_entity": "Plataforma IoT Industrial", "cardinality": "1:N", "description": "Relaci\u00f3n entre los modelos predictivos y la plataforma", "foreign_key": "id_plataforma" } ] } ], "normalization_notes": [ "La entidad Plataforma IoT Industrial tiene una clave primaria compuesta por el atributo id y el atributo nombre.", "La entidad Sensores y dispositivos edge tiene una clave primaria compuesta por el atributo id y el atributo nombre.", "La entidad Modelos predictivos tiene una clave primaria compuesta por el atributo id y el atributo nombre." ], "design_assumptions": [ "Se asume que la plataforma IoT industrial sera implementada en todas las sedes.", "Se asume que la plataforma IoT industrial sera integrada con sistemas existentes.", "Se asume que la plataforma IoT industrial sera escalable y modular." ] } } # <-- Replace with your JSON dictionary


# -----------------------------
# 2️⃣ GENERATE ER DIAGRAM IMAGE
# -----------------------------

def generate_er_diagram(er_data, output_path="er_diagram.png"):
    G = nx.DiGraph()

    for entity in er_data["entities"]:
        G.add_node(entity["name"])

        for rel in entity.get("relationships", []):
            G.add_edge(entity["name"], rel["to_entity"], label=rel["cardinality"])

    pos = nx.spring_layout(G, seed=42)

    plt.figure(figsize=(10, 8))
    nx.draw(
        G,
        pos,
        with_labels=True,
        node_size=4000,
        node_color="lightblue",
        font_size=9,
        font_weight="bold",
        arrows=True,
    )

    edge_labels = nx.get_edge_attributes(G, "label")
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    plt.title("ER Diagram - Plataforma IoT Industrial")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

    return output_path


# -----------------------------
# 3️⃣ BUILD PDF DOCUMENT
# -----------------------------

def create_pdf(data, filename="Plataforma_IoT_Industrial.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    title_style = styles["Heading1"]
    section_style = styles["Heading2"]
    normal_style = styles["BodyText"]

    # TITLE
    elements.append(Paragraph("Plataforma IoT Industrial", title_style))
    elements.append(Spacer(1, 0.3 * inch))

    # -----------------------------
    # REQUIREMENTS SECTION
    # -----------------------------
    elements.append(Paragraph("1. Requirements", section_style))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("Business Goals:", styles["Heading3"]))
    for goal in data["requirements"]["business_goals"]:
        elements.append(Paragraph(str(goal), normal_style))
        elements.append(Spacer(1, 0.1 * inch))

    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph("Functional Requirements:", styles["Heading3"]))
    for fr in data["requirements"]["functional_requirements"]:
        elements.append(Paragraph(f"- {fr['title']}: {fr['description']}", normal_style))
        elements.append(Spacer(1, 0.1 * inch))

    elements.append(PageBreak())

    # -----------------------------
    # INCEPTION SECTION
    # -----------------------------
    elements.append(Paragraph("2. Inception", section_style))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("Product Summary:", styles["Heading3"]))
    elements.append(Paragraph(data["inception"]["product_summary"], normal_style))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("Problem Statement:", styles["Heading3"]))
    elements.append(Paragraph(data["inception"]["problem_statement"], normal_style))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("Value Proposition:", styles["Heading3"]))
    elements.append(Paragraph(data["inception"]["value_proposition"], normal_style))
    elements.append(PageBreak())

    # -----------------------------
    # ER DESIGN SECTION
    # -----------------------------
    elements.append(Paragraph("3. ER Design", section_style))
    elements.append(Spacer(1, 0.2 * inch))

    for entity in data["er_design"]["entities"]:
        elements.append(Paragraph(f"Entity: {entity['name']}", styles["Heading3"]))
        elements.append(Paragraph(entity["description"], normal_style))
        elements.append(Spacer(1, 0.1 * inch))

        elements.append(Paragraph("Attributes:", styles["Heading4"]))
        for attr in entity["attributes"]:
            elements.append(Paragraph(f"- {attr['name']} ({attr['data_type']})", normal_style))
        elements.append(Spacer(1, 0.2 * inch))

    # Generate ER Diagram
    er_image_path = generate_er_diagram(data["er_design"])

    elements.append(Paragraph("Final ER Diagram:", styles["Heading3"]))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Image(er_image_path, width=6 * inch, height=5 * inch))

    # Build PDF
    doc.build(elements)

    # Clean temporary image
    if os.path.exists(er_image_path):
        os.remove(er_image_path)


# -----------------------------
# 4️⃣ RUN
# -----------------------------

create_pdf(data)

print("PDF successfully generated!")