"""
Cybersecurity investigation tools.

These tools are called by the Investigation Agent.
The agent decides which tool should be used next.

Current tools:
    1. analyze_xai
    2. search_security_knowledge
    3. evaluate_evidence

The search_security_knowledge() tool uses
MITRE ATT&CK through the FAISS-based retriever.
"""

from rag.mitre_retriever import MitreRetriever


class CyberInvestigationTools:

    def __init__(self):
        """
        Initialize the cybersecurity investigation tools.

        MITRE ATT&CK is loaded through the FAISS-based
        retrieval system.
        """

        self.mitre_retriever = MitreRetriever()

    # ==========================================================
    # TOOL 1: XAI ANALYSIS
    # ==========================================================

    def analyze_xai(
        self,
        xai_evidence,
        network_flow
    ):
        """
        Analyze the SHAP/XAI evidence supplied by the
        ML pipeline.
        """

        important_features = []

        if not isinstance(
            xai_evidence,
            dict
        ):
            xai_evidence = {}

        # Different projects may use different names
        # for SHAP feature information.

        possible_keys = [

            "top_features",

            "important_features",

            "feature_contributions",

            "shap_values",

            "features"
        ]

        for key in possible_keys:

            value = xai_evidence.get(
                key
            )

            if value:

                important_features.append({

                    "source":
                        key,

                    "value":
                        value
                })

        return {

            "tool":
                "ANALYZE_XAI",

            "status":
                "completed",

            "important_features":
                important_features,

            "network_flow":
                network_flow
        }

    # ==========================================================
    # TOOL 2: MITRE ATT&CK SECURITY KNOWLEDGE SEARCH
    # ==========================================================

    def search_security_knowledge(
        self,
        attack_type,
        query
    ):
        """
        Search MITRE ATT&CK using semantic retrieval.

        The agent provides:
            - attack_type
            - investigation query

        The query is converted into an embedding and
        searched against the MITRE ATT&CK FAISS index.

        The LLM does NOT invent MITRE techniques.
        Retrieved techniques come from the MITRE dataset.
        """

        try:

            # --------------------------------------------------
            # Build investigation query
            # --------------------------------------------------

            search_query = (
                f"Attack type: {attack_type}. "
                f"Investigation query: {query}"
            )

            # --------------------------------------------------
            # Search MITRE ATT&CK
            # --------------------------------------------------

            results = (
                self.mitre_retriever.search(
                    search_query,
                    top_k=5
                )
            )

            # --------------------------------------------------
            # No results
            # --------------------------------------------------

            if not results:

                return {

                    "tool":
                        "SEARCH_SECURITY_KNOWLEDGE",

                    "status":
                        "no_results",

                    "attack_type":
                        attack_type,

                    "query":
                        search_query,

                    "retrieved_evidence":
                        []
                }

            # --------------------------------------------------
            # Return retrieved MITRE evidence
            # --------------------------------------------------

            return {

                "tool":
                    "SEARCH_SECURITY_KNOWLEDGE",

                "status":
                    "completed",

                "source":
                    "MITRE ATT&CK",

                "attack_type":
                    attack_type,

                "query":
                    search_query,

                "retrieved_evidence":
                    results
            }

        except Exception as e:

            return {

                "tool":
                    "SEARCH_SECURITY_KNOWLEDGE",

                "status":
                    "error",

                "attack_type":
                    attack_type,

                "query":
                    query,

                "error":
                    str(e),

                "retrieved_evidence":
                    []
            }

    # ==========================================================
    # TOOL 3: EVIDENCE EVALUATION
    # ==========================================================

    def evaluate_evidence(
        self,
        ml_prediction,
        xai_evidence,
        retrieved_evidence
    ):
        """
        Evaluate whether enough evidence is available
        to finish the investigation.

        The ML model remains the primary classifier.

        The agent uses:
            ML prediction
            +
            XAI evidence
            +
            MITRE ATT&CK evidence

        to decide whether the investigation has
        sufficient supporting information.
        """

        if not isinstance(
            ml_prediction,
            dict
        ):
            ml_prediction = {}

        if not isinstance(
            xai_evidence,
            dict
        ):
            xai_evidence = {}

        # ------------------------------------------------------
        # Extract confidence
        # ------------------------------------------------------

        confidence = ml_prediction.get(
            "confidence",
            0
        )

        try:

            confidence = float(
                confidence
            )

        except (
            TypeError,
            ValueError
        ):

            confidence = 0.0

        # ------------------------------------------------------
        # Check evidence availability
        # ------------------------------------------------------

        xai_available = bool(
            xai_evidence
        )

        retrieval_available = bool(
            retrieved_evidence
        )

        classification_status = (
            ml_prediction.get(
                "classification_status",
                "UNKNOWN"
            )
        )

        prediction = ml_prediction.get(
            "prediction",
            "UNKNOWN"
        )

        attack_type = ml_prediction.get(
            "attack_type",
            prediction
        )

        # ------------------------------------------------------
        # Known attack with strong confidence
        #
        # ML is already confident.
        # XAI must be available.
        # ------------------------------------------------------

        if (
            classification_status == "KNOWN"
            and confidence >= 80
            and xai_available
        ):

            sufficient = True

            reason = (
                "Known attack with strong ML confidence "
                "and available XAI evidence."
            )

        # ------------------------------------------------------
        # Moderate confidence
        #
        # Additional MITRE evidence is required.
        # ------------------------------------------------------

        elif (
            confidence >= 60
            and xai_available
            and retrieval_available
        ):

            sufficient = True

            reason = (
                "Moderate ML confidence supported by "
                "XAI and MITRE ATT&CK evidence."
            )

        # ------------------------------------------------------
        # Possible unseen attack
        #
        # Require XAI + retrieved evidence.
        # ------------------------------------------------------

        elif (
            classification_status
            == "POSSIBLE_UNSEEN_ATTACK"

            and retrieval_available

            and xai_available
        ):

            sufficient = True

            reason = (
                "Potential unseen attack has supporting "
                "XAI and MITRE ATT&CK evidence. "
                "The result remains an investigation "
                "hypothesis rather than confirmed classification."
            )

        # ------------------------------------------------------
        # Insufficient evidence
        # ------------------------------------------------------

        else:

            sufficient = False

            reason = (
                "Available evidence is insufficient "
                "to complete the investigation."
            )

        # ------------------------------------------------------
        # Return evaluation
        # ------------------------------------------------------

        return {

            "tool":
                "EVALUATE_EVIDENCE",

            "evidence_sufficient":
                sufficient,

            "reason":
                reason,

            "prediction":
                prediction,

            "attack_type":
                attack_type,

            "confidence":
                confidence,

            "classification_status":
                classification_status,

            "xai_available":
                xai_available,

            "retrieved_evidence_available":
                retrieval_available
        }