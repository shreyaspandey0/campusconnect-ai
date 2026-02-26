# Research Paper Diagrams

Here are the Mermaid.js diagrams for your research paper. You can render these using any Markdown editor that supports Mermaid (like VS Code, GitHub, or Obsidian) or use an online editor like [Mermaid Live Editor](https://mermaid.live/).

## Figure 1: System Architecture Diagram
This diagram illustrates the high-level components and their interactions, separated by logical layers.

```mermaid
graph TD
    %% Styling
    classDef layer fill:#f9f9f9,stroke:#333,stroke-width:2px;
    classDef component fill:#fff,stroke:#333,stroke-width:1px;
    classDef external fill:#e1f5fe,stroke:#0277bd,stroke-width:2px;
    classDef db fill:#fff3e0,stroke:#ef6c00,stroke-width:2px;

    subgraph Presentation_Layer [Presentation Layer]
        UI[Web Chat Interface<br/>(HTML/JS/CSS)]:::component
    end

    subgraph Application_Logic [Application Layer]
        Flask[Python Flask Controller<br/>(app.py)]:::component
        Auth[Input Validator &<br/>Lead Capture Regex]:::component
        RAG[RAG Logic Module<br/>(Context Scorer)]:::component
    end

    subgraph Data_Layer [Data Layer]
        SQLite[(SQLite Database<br/>Leads & Chat Logs)]:::db
        KB[Knowledge Base<br/>(.txt Files)]:::db
    end

    subgraph External_Service [External Service]
        Groq[Groq API<br/>Llama-3 Inference]:::external
    end

    %% Connections
    UI <-->|REST API (JSON)| Flask
    Flask --> Auth
    Auth -->|Valid Data| RAG
    Auth -->|Store Phone#| SQLite
    RAG <-->|Read Chunks| KB
    RAG <-->|Log History| SQLite
    RAG <-->|Prompt + Context| Groq

    class Presentation_Layer,Application_Logic,Data_Layer,External_Service layer;
```

---

## Figure 2: Query Resolution Logic (Technique Flowchart)
This flowchart details the step-by-step logic defined in Section 6.2, including the scoring algorithm and the offline fallback mechanism.

```mermaid
flowchart TD
    %% Nodes
    Start([User Input])
    Tokenize[Tokenization &<br/>Keyword Extraction]
    ScanChunks[Scan Document Chunks<br/>(college_data.txt / website_data.txt)]
    
    subgraph Scoring_System [Context Scoring Algorithm]
        direction TB
        CalcUnique[Calculate Unique Matches (U)]
        CalcTotal[Calculate Total Matches (T)]
        ApplyFormula[Apply Formula:<br/>Score = U*3 + T]
        Sort[Sort & Select Top 5 Chunks]
    end

    Assemble[Assemble Prompt:<br/>System Inst + Context + Query]
    CallAPI[Call Groq API<br/>(Llama-3)]
    
    CheckStatus{API Success?}
    
    SuccessResponse[Generate AI Response]
    CheckError{Error Type?}
    
    OfflineFallback[<b>OFFSET MODE TRIGGERED</b><br/>Select Highest Scoring<br/>Local Chunk]
    
    FinalOutput([Final Response to User])

    %% Edges
    Start --> Tokenize
    Tokenize --> ScanChunks
    ScanChunks --> Scoring_System
    
    CalcUnique --> CalcTotal
    CalcTotal --> ApplyFormula
    ApplyFormula --> Sort
    
    Sort --> Assemble
    Assemble --> CallAPI
    
    CallAPI --> CheckStatus
    CheckStatus -- Yes --> SuccessResponse
    CheckStatus -- No --> CheckError
    
    CheckError -- "429 (Rate Limit) / 503" --> OfflineFallback
    CheckError -- "Other Error" --> OfflineFallback
    
    SuccessResponse --> FinalOutput
    OfflineFallback -->|Append [Offline Mode] Tag| FinalOutput

    %% Styling
    style Start fill:#dcedc8,stroke:#33691e,stroke-width:2px
    style FinalOutput fill:#dcedc8,stroke:#33691e,stroke-width:2px
    style OfflineFallback fill:#ffccbc,stroke:#bf360c,stroke-width:2px
    style CheckStatus fill:#fff9c4,stroke:#fbc02d,stroke-width:2px
    style CheckError fill:#fff9c4,stroke:#fbc02d,stroke-width:2px
```
