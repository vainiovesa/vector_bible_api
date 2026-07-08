from pgvector.sqlalchemy import VECTOR
from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, Boolean, func
from sqlalchemy.orm import relationship

from db import Base


EMBEDDING_DIMENSIONS = 1536


class Translation(Base):
	__tablename__ = "translations"

	id = Column(Integer, primary_key=True, index=True)
	code = Column(String(32), nullable=False, unique=True, index=True)
	name = Column(String(128), nullable=False)
	created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

	verses = relationship("BibleVerse", back_populates="translation", cascade="all, delete-orphan")


class BibleVerse(Base):
	__tablename__ = "bible_verses"

	id = Column(Integer, primary_key=True, index=True)
	translation_id = Column(Integer, ForeignKey("translations.id", ondelete="CASCADE"), nullable=False, index=True)
	book = Column(String(64), nullable=False, index=True)
	chapter = Column(Integer, nullable=False, index=True)
	verse = Column(Integer, nullable=False, index=True)
	text = Column(Text, nullable=False)
	embedding = Column(VECTOR(EMBEDDING_DIMENSIONS), nullable=False)
	created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

	translation = relationship("Translation", back_populates="verses")

	__table_args__ = (
		UniqueConstraint("translation_id", "book", "chapter", "verse", name="uq_bible_verse_reference"),
		Index(
            "ix_verses_embedding_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_ops={"embedding": "vector_cosine_ops"},
            postgresql_with={
                "m": 16,
                "ef_construction": 64,
            },
		),
	)


class BibleChunk(Base):
	__tablename__ = "bible_chunks"

	id = Column(Integer, primary_key=True, index=True)
	begin_verse_id = Column(Integer, ForeignKey("bible_verses.id", ondelete="CASCADE"), nullable=False, index=True)
	end_verse_id = Column(Integer, ForeignKey("bible_verses.id", ondelete="CASCADE"), nullable=False, index=True)
	embedding = Column(VECTOR(EMBEDDING_DIMENSIONS), nullable=False)
	created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

	__table_args__ = (
		UniqueConstraint("begin_verse_id", "end_verse_id", name="uq_bible_chunk_reference"),
		Index(
            "ix_chunks_embedding_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_ops={"embedding": "vector_cosine_ops"},
            postgresql_with={
                "m": 16,
                "ef_construction": 64,
            },
		),
	)


class Book(Base):
	__tablename__ = "books"

	name = Column(String(64), primary_key=True)
	canonical_order = Column(Integer, nullable=False)
	old_testament = Column(Boolean, nullable=False)
	created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

	__table_args__ = (
		UniqueConstraint("name", name="uq_book_name"),
	)
