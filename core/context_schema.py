import json


class ContextSchema:
    """
    CRME Context Schema v1.0

    Defines transferable research state format.
    """

    VERSION = "1.0"



    @staticmethod
    def validate(context):

        required = [

            "crme_version",

            "project",

            "summary",

            "research_state",

            "knowledge_graph",

            "transfer_info"

        ]


        missing = [

            key for key in required
            if key not in context

        ]


        return {

            "valid":
                len(missing) == 0,


            "missing":

                missing,


            "version":

                context.get(
                    "crme_version"
                )

        }



    @staticmethod
    def save_schema(path):

        schema = {

            "name":
                "CRME Context Transfer Schema",


            "version":
                ContextSchema.VERSION,


            "required_fields":

            [

                "project",

                "summary",

                "research_state",

                "knowledge_graph",

                "transfer_info"

            ]

        }


        with open(
            path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                schema,
                f,
                indent=2
            )


        return path
