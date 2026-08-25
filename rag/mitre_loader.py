import json
import os
import requests


class MitreAttackLoader:

    MITRE_URL = (
        "https://raw.githubusercontent.com/"
        "mitre-attack/attack-stix-data/master/"
        "enterprise-attack/enterprise-attack.json"
    )

    def __init__(self):

        self.base_dir = os.path.dirname(
            os.path.abspath(__file__)
        )

        self.data_dir = os.path.join(
            self.base_dir,
            "data"
        )

        self.data_path = os.path.join(
            self.data_dir,
            "enterprise-attack.json"
        )

        os.makedirs(
            self.data_dir,
            exist_ok=True
        )

    # ==========================================================
    # DOWNLOAD MITRE ATT&CK
    # ==========================================================

    def download(self):

        print(
            "\nDownloading MITRE ATT&CK Enterprise data..."
        )

        response = requests.get(
            self.MITRE_URL,
            timeout=60
        )

        response.raise_for_status()

        with open(
            self.data_path,
            "wb"
        ) as file:

            file.write(
                response.content
            )

        print(
            "MITRE ATT&CK data downloaded successfully."
        )

    # ==========================================================
    # LOAD DATA
    # ==========================================================

    def load(self):

        if not os.path.exists(
            self.data_path
        ):

            self.download()

        with open(
            self.data_path,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        return data

    # ==========================================================
    # EXTRACT ATTACK TECHNIQUES
    # ==========================================================

    def get_techniques(self):

        data = self.load()

        techniques = []

        for obj in data.get(
            "objects",
            []
        ):

            if obj.get("type") != "attack-pattern":
                continue

            if obj.get(
                "revoked",
                False
            ):
                continue

            if obj.get(
                "x_mitre_deprecated",
                False
            ):
                continue

            name = obj.get(
                "name",
                ""
            )

            description = obj.get(
                "description",
                ""
            )

            external_id = None

            for reference in obj.get(
                "external_references",
                []
            ):

                if (
                    reference.get(
                        "source_name"
                    )
                    == "mitre-attack"
                ):

                    external_id = (
                        reference.get(
                            "external_id"
                        )
                    )

                    break

            if not external_id:
                continue

            kill_chain_phases = []

            for phase in obj.get(
                "kill_chain_phases",
                []
            ):

                kill_chain_phases.append(
                    phase.get(
                        "phase_name",
                        ""
                    )
                )

            techniques.append({

                "id":
                    external_id,

                "name":
                    name,

                "description":
                    description,

                "tactics":
                    kill_chain_phases
            })

        return techniques