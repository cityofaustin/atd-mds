#
#
#

from string import Template


class MDSGraphQLRequest:

    model = {
        "query_name": None,
        "query_type": None,
        "query_arguments": None,
        "table_name": None,
        "table_fields": {},
        "table_values": {}
    }

    def get_model(self):
        return self.model

    def set_model_value(self, model_property, value):
        self.model[model_property] = value

    def get_model_value(self, model_property, default_value):
        return self.model.get(model_property, default_value)

    def generate_query(self):

        template = Template("""
        $query_type $query_name $query_arguments {
            $table_name {
                $table_values
            }
        }
        """)

        return template.substitute(query_type=self.get_model_value("query_type", "query"))


