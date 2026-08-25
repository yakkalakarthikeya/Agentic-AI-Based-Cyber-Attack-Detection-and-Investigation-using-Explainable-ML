import faiss

from sentence_transformers import (
    SentenceTransformer
)

from rag.mitre_loader import (
    MitreAttackLoader
)


class MitreRetriever:

    def __init__(self):

        print(
            "\nInitializing MITRE ATT&CK retriever..."
        )

        self.loader = MitreAttackLoader()

        self.embedding_model = (
            SentenceTransformer(
                "all-MiniLM-L6-v2"
            )
        )

        self.techniques = (
            self.loader.get_techniques()
        )

        if not self.techniques:

            raise RuntimeError(
                "No MITRE ATT&CK techniques found."
            )

        self.documents = (
            self._create_documents()
        )

        self.index = (
            self._build_faiss_index()
        )

        print(
            f"Loaded {len(self.techniques)} "
            "MITRE ATT&CK techniques."
        )

    # ==========================================================
    # CREATE SEARCH DOCUMENTS
    # ==========================================================

    def _create_documents(self):

        documents = []

        for technique in self.techniques:

            document = f"""
MITRE ATT&CK TECHNIQUE

Technique ID:
{technique['id']}

Technique Name:
{technique['name']}

Tactics:
{', '.join(technique['tactics'])}

Description:
{technique['description']}
"""

            documents.append(
                document.strip()
            )

        return documents

    # ==========================================================
    # BUILD FAISS INDEX
    # ==========================================================

    def _build_faiss_index(self):

        embeddings = (
            self.embedding_model.encode(
                self.documents,
                convert_to_numpy=True,
                show_progress_bar=True
            )
        )

        embeddings = embeddings.astype(
            "float32"
        )

        # Normalize vectors so inner product
        # behaves like cosine similarity.

        faiss.normalize_L2(
            embeddings
        )

        dimension = embeddings.shape[1]

        index = faiss.IndexFlatIP(
            dimension
        )

        index.add(
            embeddings
        )

        return index

    # ==========================================================
    # SEARCH MITRE ATT&CK
    # ==========================================================

    def search(
        self,
        query,
        top_k=5
    ):

        if not query:
            return []

        query_embedding = (
            self.embedding_model.encode(
                [query],
                convert_to_numpy=True
            )
        )

        query_embedding = (
            query_embedding.astype(
                "float32"
            )
        )

        faiss.normalize_L2(
            query_embedding
        )

        scores, indices = (
            self.index.search(
                query_embedding,
                top_k
            )
        )

        results = []

        for score, index in zip(
            scores[0],
            indices[0]
        ):

            if index < 0:
                continue

            technique = (
                self.techniques[index]
            )

            results.append({

                "technique_id":
                    technique["id"],

                "technique_name":
                    technique["name"],

                "tactics":
                    technique["tactics"],

                "description":
                    technique["description"],

                "similarity":
                    float(score)
            })

        return results