# Copyright 2020 John Reese
# Licensed under the MIT license

import textwrap

from jinja2 import Template

from .project import Project


class GeneratedFile:
    FILENAME: str = "FAKE.md"
    TEMPLATE: str = "FAKE FILE, DO NOT COMMIT!"

    def __init__(self, project: Project):
        self.project = project

    def generate(self) -> str:
        tags = self.project.tags
        template = Template(textwrap.dedent(self.TEMPLATE))
        output = template.render(project=self.project, tags=tags, len=len)
        return output


class Changelog(GeneratedFile):
    FILENAME = "CHANGELOG.md"
    TEMPLATE = """
        {{- project.name }}
        {{ "=" * len(project.name) }}
        {% for tag in tags %}
        {{ tag.name }}
        {{ "-" * len(tag.name) }}

        {{ tag.message if tag.message else "" }}
        {% if tag.shortlog -%}
        ```
        $ {{ tag.shortlog_cmd }}
        {{ tag.shortlog }}
        ```
        {%- endif %}

        {% endfor -%}
    """


class Contributers(GeneratedFile):
    FILENAME = "CONTRIBUTERS"
    TEMPLATE = """
        Contributers
        ============

        {{ project.shortlog }}
        """
