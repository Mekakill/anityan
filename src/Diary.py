import asyncio
import json
from pathlib import Path
from typing import List, Optional, Dict, Any, Callable
from dataclasses import dataclass, field
import numpy as np
from aiohttp import ClientSession


@dataclass
class Entry:
    """Simple diary entry"""
    id: str
    text: str


@dataclass
class EntryMetadata:
    """Extended entry metadata"""
    score: float = 0.0
    confidence: float = 0.0
    last_used: str = "never"
    usage_count: int = 0
    embedding: np.ndarray = field(default_factory=lambda: np.array([]))


@dataclass
class EntryEx:
    """Extended diary entry with metadata"""
    id: str
    metadata: EntryMetadata = field(default_factory=EntryMetadata)
    freeform_body: str = ""
    
    def increment_usage_count(self):
        self.metadata.usage_count += 1
        self.metadata.last_used = str(datetime.now())


@dataclass
class EntryExAndRelatedness:
    """Entry with relatedness score"""
    entry: EntryEx
    relatedness: float = 0.0
    
    def __lt__(self, other):
        return self.relatedness > other.relatedness


class Diary:
    """RAG-based diary system with embedding search"""
    
    def __init__(self, diary_dir: str = "diary"):
        self.diary_dir = Path(diary_dir)
        self.diary_dir.mkdir(parents=True, exist_ok=True)
        self._cache: Optional[List[EntryEx]] = None
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    @staticmethod
    def read(diary_dir: Path) -> List[Entry]:
        """Read all markdown files from diary directory"""
        entries = []
        for file_path in diary_dir.glob("*.md"):
            text = file_path.read_text(encoding='utf-8')
            entry_id = file_path.stem
            entries.append(Entry(id=entry_id, text=text))
        return entries
    
    def save(self, entry: Entry):
        """Save simple entry to disk"""
        entry_path = self.diary_dir / f"{entry.id}.md"
        entry_path.write_text(entry.text, encoding='utf-8')
    
    def save_ex(self, entry: EntryEx):
        """Save extended entry with metadata"""
        # Save metadata and body separately
        metadata_path = self.diary_dir / f"{entry.id}_meta.json"
        body_path = self.diary_dir / f"{entry.id}.md"
        
        with open(metadata_path, 'w') as f:
            json.dump({
                "score": entry.metadata.score,
                "confidence": entry.metadata.confidence,
                "last_used": entry.metadata.last_used,
                "usage_count": entry.metadata.usage_count,
                "embedding": entry.metadata.embedding.tolist()
            }, f)
        
        with open(body_path, 'w') as f:
            f.write(entry.freeform_body)
    
    async def query(self, query_embedding: np.ndarray, 
                   opts: Optional[Dict[str, Any]] = None) -> List[EntryExAndRelatedness]:
        """Query diary for related entries using embedding similarity"""
        if opts is None:
            opts = {}
        
        max_entries = opts.get('max_entry_count', 10)
        confidence_factor = opts.get('confidence_factor', 0.01)
        
        results = []
        cache_dir = self.diary_dir / "cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        for entry_file in self.diary_dir.glob("*.md"):
            entry_id = entry_file.stem
            
            # Load metadata if exists
            meta_path = self.diary_dir / f"{entry_id}_meta.json"
            if meta_path.exists():
                with open(meta_path, 'r') as f:
                    meta_data = json.load(f)
                embedding = np.array(meta_data.get('embedding', []))
                confidence = meta_data.get('confidence', 0.0)
            else:
                # Generate embedding if not exists
                embedding = await self._generate_embedding(entry_file.read_text())
            
            if len(embedding) != len(query_embedding):
                continue
            
            relatedness = (cosine_similarity(query_embedding, embedding) + 1.0) / 2.0
            relatedness += confidence * confidence_factor
            
            results.append(EntryExAndRelatedness(
                entry=EntryEx(id=entry_id),
                relatedness=relatedness
            ))
        
        # Sort by relatedness and return top results
        results.sort()
        return results[:max_entries]
    
    async def _generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for text using sentence-transformers"""
        embedding = self.embedding_model.encode(text).tolist()
        
        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        return np.array(embedding)
    
    def reload(self):
        """Reload diary from disk"""
        self._cache = None
    
    @property
    def list(self) -> List[EntryEx]:
        """Get cached diary entries"""
        if self._cache is None:
            self._cache = []
        
        return self._cache