import re
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class Chunk:
    content: str
    metadata: Dict[str, Any]

class ChunkingService:
    @staticmethod
    def chunk_resume(text: str, employee_id: int = None) -> List[Chunk]:
        """
        Split a resume into semantic sections based on common headings.
        If no sections are detected, or if sections are too large, fall back to sliding window chunking.
        """
        if not text or not text.strip():
            return []

        # Common resume section patterns
        # Look for section headers like "PROFESSIONAL EXPERIENCE", "SKILLS", "EDUCATION", "SUMMARY", "PROJECTS"
        # We look for lines starting with these keywords (case-insensitive) that might be headers
        sections_regex = re.compile(
            r'^(?:'
            r'work\s+experience|professional\s+experience|experience|'
            r'skills|technical\s+skills|core\s+competencies|'
            r'education|academic\s+background|'
            r'projects|key\s+projects|'
            r'summary|professional\s+summary|profile|about\s+me'
            r')$',
            re.IGNORECASE | re.MULTILINE
        )

        lines = text.split('\n')
        chunks = []
        current_section = "general"
        current_lines = []
        chunk_idx = 0

        for line in lines:
            stripped = line.strip()
            # If line matches a heading, flush the previous section and start a new one
            if sections_regex.match(stripped):
                if current_lines:
                    content = "\n".join(current_lines).strip()
                    if content:
                        chunks.append(Chunk(
                            content=content,
                            metadata={
                                "section": current_section.lower(),
                                "chunk_index": chunk_idx,
                                "source_type": "resume",
                                "source_id": employee_id
                            }
                        ))
                        chunk_idx += 1
                current_section = stripped
                current_lines = [line]
            else:
                current_lines.append(line)

        # Flush the last section
        if current_lines:
            content = "\n".join(current_lines).strip()
            if content:
                chunks.append(Chunk(
                    content=content,
                    metadata={
                        "section": current_section.lower(),
                        "chunk_index": chunk_idx,
                        "source_type": "resume",
                        "source_id": employee_id
                    }
                ))

        # Post-process: If we only got one "general" chunk or if any chunk is extremely large (> 1500 chars),
        # split those chunks using a sliding window so that search remains fine-grained.
        refined_chunks = []
        refined_idx = 0
        for chunk in chunks:
            if len(chunk.content) > 1500:
                # Split large chunk into smaller parts
                sub_chunks = ChunkingService.sliding_window_chunk(
                    text=chunk.content,
                    chunk_size=1000,
                    overlap=150
                )
                for sub_text in sub_chunks:
                    refined_chunks.append(Chunk(
                        content=sub_text,
                        metadata={
                            "section": chunk.metadata["section"],
                            "chunk_index": refined_idx,
                            "source_type": "resume",
                            "source_id": employee_id,
                            "is_sub_chunk": True
                        }
                    ))
                    refined_idx += 1
            else:
                chunk.metadata["chunk_index"] = refined_idx
                refined_chunks.append(chunk)
                refined_idx += 1

        return refined_chunks

    @staticmethod
    def sliding_window_chunk(text: str, chunk_size: int = 1000, overlap: int = 150) -> List[str]:
        """
        Split text into overlapping character windows, preserving words.
        """
        if not text:
            return []

        words = text.split()
        chunks = []
        current_chunk = []
        current_len = 0

        for word in words:
            current_chunk.append(word)
            current_len += len(word) + 1  # count spaces
            
            if current_len >= chunk_size:
                chunks.append(" ".join(current_chunk))
                # Retain overlap words
                overlap_len = 0
                overlap_words = []
                for w in reversed(current_chunk):
                    overlap_words.insert(0, w)
                    overlap_len += len(w) + 1
                    if overlap_len >= overlap:
                        break
                current_chunk = overlap_words
                current_len = overlap_len

        if current_chunk and " ".join(current_chunk).strip():
            chunks.append(" ".join(current_chunk))

        return chunks
