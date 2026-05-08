export interface Project {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
  document_count: number;
  latest_workflow_status: "running" | "completed" | "failed" | null;
}

export interface Document {
  id: string;
  project_id: string;
  filename: string;
  format: "pdf" | "docx" | "md" | "txt" | "xlsx";
  upload_status: "pending" | "uploaded" | "processing" | "ready" | "failed";
  spark_document_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface Workflow {
  id: string;
  project_id: string;
  spark_workflow_id: string;
  spark_project_id: string;
  status: "running" | "completed" | "failed";
  started_at: string;
  completed_at: string | null;
}

export interface ProjectDetail extends Project {
  documents: Document[];
  workflows: Workflow[];
}

export type ResultType = "consolidation" | "contradiction" | "summary";

export interface ConsolidationResult {
  id: string;
  project_id: string;
  query: string;
  result_type: ResultType;
  result_content: string;
  source_documents: string[];
  created_at: string;
}
