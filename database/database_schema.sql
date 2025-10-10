CREATE EXTENSION IF NOT EXISTS vector;


-- Schema: kb_user
CREATE SCHEMA kb_user;

CREATE TABLE kb_user.users (
                               user_id uuid PRIMARY KEY,
                               email VARCHAR(100) UNIQUE NOT NULL,
                               password_hash VARCHAR(255) NOT NULL,
                               full_name VARCHAR(100),
                               role VARCHAR(50),              -- Admin | User
                               email_verified BOOLEAN,
                               is_active BOOLEAN,
                               created_at TIMESTAMP,
                               updated_at TIMESTAMP 
);



-- Schema: kb_project
CREATE SCHEMA kb_project;

CREATE TABLE kb_project.projects (
                                     project_id uuid PRIMARY KEY,
                                     name VARCHAR(255) NOT NULL,
                                     description TEXT,
                                     status VARCHAR(50),            -- active | locked | deleted
                                     locked_by uuid,
                                     locked_at TIMESTAMP,
                                     lock_reason TEXT,
                                     can_restore BOOLEAN,
                                     created_at TIMESTAMP ,
                                     updated_at TIMESTAMP
);

CREATE TABLE kb_project.project_members (
                                            project_member_id uuid PRIMARY KEY,
                                            user_id uuid NOT NULL,
                                            project_id uuid NOT NULL,
                                            project_role VARCHAR(50),      -- Owner | Member
                                            is_creator BOOLEAN,
                                            joined_at TIMESTAMP ,
                                            removed_at TIMESTAMP,
                                            FOREIGN KEY (project_id) REFERENCES kb_project.projects(project_id)
);

CREATE TABLE kb_project.folders (
                                    folder_id uuid PRIMARY KEY,
                                    project_id uuid NOT NULL,
                                    parent_folder_id uuid,
                                    name VARCHAR(255) NOT NULL,
                                    path TEXT,
                                    created_by uuid,
                                    created_at TIMESTAMP ,
                                    updated_at TIMESTAMP ,
                                    FOREIGN KEY (project_id) REFERENCES kb_project.projects(project_id),
                                    FOREIGN KEY (parent_folder_id) REFERENCES kb_project.folders(folder_id)
);

CREATE TABLE kb_project.documents (
                                      document_id uuid PRIMARY KEY,
                                      uploaded_by uuid NOT NULL,
                                      project_id uuid NOT NULL,
                                      folder_id uuid,
                                      name VARCHAR(255) NOT NULL,
                                      file_path TEXT,                 -- S3 path
                                      file_type VARCHAR(20),          -- PDF | MD | TXT
                                      metadata JSONB,
                                      uploaded_at TIMESTAMP ,
                                      FOREIGN KEY (project_id) REFERENCES kb_project.projects(project_id),
                                      FOREIGN KEY (folder_id) REFERENCES kb_project.folders(folder_id)
);

CREATE TABLE kb_project.videos (
                                   video_id uuid PRIMARY KEY,
                                   uploaded_by uuid NOT NULL,
                                   project_id uuid NOT NULL,
                                   folder_id uuid,
                                   name VARCHAR(255) NOT NULL,
                                   file_path TEXT,
                                   file_type VARCHAR(20),          -- MP4 | MOV | AVI
                                   transcript TEXT,
                                   metadata JSONB,
                                   uploaded_at TIMESTAMP ,
                                   FOREIGN KEY (project_id) REFERENCES kb_project.projects(project_id),
                                   FOREIGN KEY (folder_id) REFERENCES kb_project.folders(folder_id)
);




-- Schema: kb_chat
CREATE SCHEMA kb_chat;

CREATE TABLE kb_chat.document_chunks (
                                         chunk_id uuid PRIMARY KEY,
                                         document_id uuid NOT NULL,
                                         content TEXT NOT NULL,
                                         embedding vector,
                                         chunk_index INTEGER,
                                         metadata JSONB
);

CREATE TABLE kb_chat.video_chunks (
                                      chunk_id uuid PRIMARY KEY,
                                      video_id uuid NOT NULL,
                                      transcript_chunk TEXT NOT NULL,
                                      embedding vector,
                                      chunk_index INTEGER,
                                      timestamp_start FLOAT,
                                      timestamp_end FLOAT,
                                      metadata JSONB
);

CREATE TABLE kb_chat.chat_messages (
                                       chat_message_id uuid PRIMARY KEY,
                                       user_id uuid NOT NULL,
                                       project_id uuid NOT NULL,
                                       user_message TEXT NOT NULL,
                                       ai_response TEXT,
                                       source_references JSONB,
                                       created_at TIMESTAMP
);

-- drop schema kb_project cascade;
-- drop schema kb_user cascade;