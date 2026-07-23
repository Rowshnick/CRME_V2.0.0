import csv
import os


class CSVImporter:
    """
    Import CSV datasets for CRME Evaluation
    """

    def load(self, path):

        if not os.path.exists(path):
            raise FileNotFoundError(
                path
            )


        records = []

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:

            reader = csv.DictReader(f)

            for row in reader:
                records.append(row)


        return records



    def schema(self, path):

        data = self.load(path)

        if not data:
            return {}

        return {
            "features":
                list(data[0].keys()),

            "samples":
                len(data)
        }

