import json
import os


class JSONImporter:
    """
    Import JSON datasets for CRME Evaluation
    """


    def load(self, path):

        if not os.path.exists(path):
            raise FileNotFoundError(
                path
            )


        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)



    def schema(self, path):

        data = self.load(path)


        if isinstance(data, list):

            samples = len(data)

            features = (
                list(data[0].keys())
                if samples > 0
                else []
            )


            return {
                "samples": samples,
                "features": features
            }


        return {
            "type":
                type(data).__name__
        }

