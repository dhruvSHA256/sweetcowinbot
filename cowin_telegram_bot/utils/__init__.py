from jinja2 import Template
from typing import Dict, Any


def render_template(
    centers: dict,
    pincode: int,
    min_age_limit: int,
    show_age: bool = True,
    show_vaccine: bool = True,
):
    """
    generate formatted message to send on telegram

    :param centers dict: [TODO:description]
    :param pincode int: [TODO:description]
    :param min_age_limit int: [TODO:description]
    :param show_age bool: [TODO:description]
    :param show_vaccine bool: [TODO:description]
    """
    if min_age_limit == 18:
        filtered_centers: Dict[str, Any] = {}
        for center_name, slots in centers.items():
            for slot in slots:
                if slot["min_age_limit"] == min_age_limit:
                    if center_name in filtered_centers:
                        filtered_centers[center_name].append(slot)
                    else:
                        filtered_centers[center_name] = [slot]
    else:
        filtered_centers = centers

    if filtered_centers:
        template = """
*Avalilable Slots in {{pincode}} for {{min_age_limit}}+  💉  *\n\n {% for center_name,slots in centers.items()%} *{{center_name}} :*\n {% for slot in slots %}     • {{ slot['date'].strftime("%d %B, %a") }} : {{ slot['available_capacity'] }}    ({{slot['min_age_limit']}}+)\n {% endfor %}
{% endfor %}
            """
        message = Template(template).render(
            centers=filtered_centers, pincode=pincode, min_age_limit=min_age_limit
        )
    else:
        message = f"No vaccination session found for {min_age_limit}+ in {pincode}\
                in near future"
    return message
