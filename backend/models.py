from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Boolean, func
from sqlalchemy.orm import declarative_base, relationship
import datetime

Base = declarative_base()

# Minimalistic approach to student data (Data Minimization Principle)
class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    # Solo el identificador mínimo necesario. Podría ser un seudónimo si se requiere anonimización.
    student_identifier = Column(String, unique=True, index=True, nullable=False)
    
    # Campo JSON dinámico para guardar únicamente las métricas que el profesor 
    # haya autorizado subir (ej. asistencias, calificaciones específicas)
    analytics_data = Column(JSON, default={})

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    upload_date = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Metadata extraída (autorizada por el humano)
    metadata_json = Column(JSON, default={})

class AgentHistory(Base):
    __tablename__ = "agent_history"

    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(String, index=True)
    subject_name = Column(String, index=True)
    executed_at = Column(DateTime, default=func.now())
    details = Column(String)
    files_generated = Column(String) # JSON list of file names/paths

class AuditLog(Base):
    __tablename__ = "audit_logs"
    """
    Registro estricto de trazabilidad para cumplir con normas ISO.
    """
    id = Column(Integer, primary_key=True, index=True)
    action = Column(String, nullable=False) # e.g., "UPLOAD_DOCUMENT", "AUTHORIZE_SCHEMA", "DELETE_RECORD"
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(String, nullable=False) # ID del profesor (Google OAuth)
    details = Column(JSON, default={})
