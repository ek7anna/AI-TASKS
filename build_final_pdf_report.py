"""
build_final_pdf_report.py - Generates an exhaustive, multi-page, publication-grade PDF documentation report
containing ALL code walkthroughs, unabridged source code listings, technical changes from yesterday's addendum,
official RAGAS benchmark results, LangSmith telemetry evidence, guardrails architecture, test cases, and all embedded screenshots.
"""

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, HRFlowable, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

PDF_FILENAME = "PPT_Semantic_RAG_Guardrails_and_RAGAS_Evaluation_Report.pdf"
SCREENSHOT_DIR = r"C:\Users\EileneAnnaKuriakose\ppt_rag_evaluation\screenshots"

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and print total page count."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            return  # Skip cover page headers/footers
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#1A365D"))

        # Header
        self.drawString(54, 11 * 72 - 36, "PPT Semantic RAG Chatbot — Official RAGAS & Guardrails Master Technical Report")
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.5)
        self.line(54, 11 * 72 - 42, 8.5 * 72 - 54, 11 * 72 - 42)

        # Footer
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#4A5568"))
        self.drawRightString(8.5 * 72 - 54, 36, page_str)
        self.drawString(54, 36, "Comprehensive Technical Documentation & Empirical Evidence")
        self.line(54, 46, 8.5 * 72 - 54, 46)
        self.restoreState()

def create_pdf_report():
    pdf_path = os.path.join(r"C:\Users\EileneAnnaKuriakose\ppt_rag_evaluation", PDF_FILENAME)
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#1A365D"),
        spaceAfter=12
    )

    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#2B6CB0"),
        spaceAfter=20
    )

    meta_style = ParagraphStyle(
        'CoverMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#4A5568")
    )

    h1_style = ParagraphStyle(
        'CustomH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=colors.HexColor("#1A365D"),
        spaceBefore=18,
        spaceAfter=10,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'CustomH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=15,
        textColor=colors.HexColor("#2B6CB0"),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13.5,
        textColor=colors.HexColor("#2D3748"),
        spaceAfter=8
    )

    code_style = ParagraphStyle(
        'CustomCode',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#1A202C")
    )

    caption_style = ParagraphStyle(
        'CaptionStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#4A5568"),
        alignment=1,
        spaceAfter=10
    )

    elements = []

    # -------------------------------------------------------------------------
    # COVER PAGE
    # -------------------------------------------------------------------------
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("PPT Semantic RAG Chatbot", title_style))
    elements.append(Paragraph("Official RAGAS v0.4.3 Evaluation, LangSmith Telemetry & LangChain Output Guardrails Implementation", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#2B6CB0"), spaceAfter=20))

    meta_text = """
    <b>Project Location:</b> C:\\Users\\EileneAnnaKuriakose\\ppt_rag_evaluation<br/>
    <b>Technical Scope:</b> Full Pipeline Refactoring, Official RAGAS Library Evaluation, LangSmith Feedback Logging, LangChain Output Validation & Guardrail-Memory Architecture<br/>
    <b>Vector Database:</b> Apache Solr (PPT slide content index, 384-dimensional dense vectors)<br/>
    <b>Models:</b> Ollama <code>llama3.2</code> (Chatbot Generator), Ollama <code>mistral</code> (format='json' RAGAS Judge), HuggingFace <code>sentence-transformers/all-MiniLM-L6-v2</code><br/>
    <b>Report Generation Date:</b> July 27, 2026<br/>
    """
    elements.append(Paragraph(meta_text, meta_style))
    elements.append(Spacer(1, 20))

    exec_summary = """
    <b>Executive Summary:</b><br/>
    This comprehensive, publication-grade technical report documents the complete implementation, architecture refactoring, official evaluation, guardrails integration, and empirical verification across all required assignment tasks:
    <br/><br/>
    <b>1. Task 1 — Official RAGAS Evaluation & LangSmith Feedback Logging:</b><br/>
    Upgraded the evaluation pipeline from raw cosine similarity proxies to the <b>official RAGAS PyPI library (v0.4.3)</b>. Configured an offline local <code>mistral</code> judge model (format='json') to evaluate Faithfulness, Context Precision, Context Recall, and Answer Relevancy across 5 test questions, logging real feedback metrics directly to LangSmith project <code>PPT-Semantic-RAG-Evaluation</code> (achieving an <b>Overall RAGAS Benchmark Score of 0.774</b>).
    <br/><br/>
    <b>2. Task 2 — LLM Guardrails Implementation:</b><br/>
    Integrated <b>LangChain-native output validators</b> (<code>LangChainOutputValidator</code> subclassing <code>StrOutputParser</code> and <code>OutputParserException</code>) combined with embedded MiniLM vector guardrails. Fixed guardrail-memory integration so prompt-injection checks evaluate only current raw user queries, preventing history poisoning and allowing multi-turn conversational follow-ups.
    """
    elements.append(Paragraph(exec_summary, body_style))
    elements.append(PageBreak())

    # -------------------------------------------------------------------------
    # TABLE OF CONTENTS & ARCHITECTURE OVERVIEW
    # -------------------------------------------------------------------------
    elements.append(Paragraph("Table of Contents & Architecture Overview", h1_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E0"), spaceAfter=12))

    toc_text = """
    <b>Table of Contents:</b>
    <ol>
      <li><b>Purpose & Scope of This Document</b></li>
      <li><b>Full Codebase Refactoring & Modularity Overview</b></li>
      <li><b>Part 1: Official RAGAS v0.4.3 Evaluation & LangSmith Telemetry</b>
        <ul>
          <li>3.1 Upgrades from Yesterday's Addendum (PDF)</li>
          <li>3.2 Evaluation Script Walkthrough (evaluate_ragas.py)</li>
          <li>3.3 Test Questions, Retrieved Solr Chunks & Ollama Outputs</li>
          <li>3.4 Empirical RAGAS Benchmark Results Table & Summary Averages</li>
          <li>3.5 Failure Case Analysis & Production Remediation Plan</li>
          <li>3.6 LangSmith Telemetry & Trace Evidence</li>
        </ul>
      </li>
      <li><b>Part 2: LLM Guardrails Implementation & Memory Integration</b>
        <ul>
          <li>4.1 Framework Choice & Architecture Rationale</li>
          <li>4.2 Four Protection Categories Implemented</li>
          <li>4.3 Guardrail-Memory Integration Architecture</li>
          <li>4.4 Sequential Session Test Cases & Verification Evidence</li>
          <li>4.5 Automated Guardrail Test Suite Results (python test_guardrails.py)</li>
          <li>4.6 Framework Limitations Found</li>
        </ul>
      </li>
      <li><b>Part 3: Complete Source Code Appendices</b> (Unabridged Code Listings)</li>
    </ol>
    """
    elements.append(Paragraph(toc_text, body_style))
    elements.append(Spacer(1, 15))

    # -------------------------------------------------------------------------
    # PART 1: OFFICIAL RAGAS EVALUATION & LANGSMITH TELEMETRY
    # -------------------------------------------------------------------------
    elements.append(Paragraph("Part 1: Official RAGAS Evaluation & LangSmith Telemetry", h1_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E0"), spaceAfter=12))

    p1_intro = """
    <b>3.1 Upgrades from Yesterday's Addendum (PDF)</b><br/>
    Yesterday's documentation described an initial evaluation prototype (<code>SCRIPT VERSION: pure-embedding-cosine-sim-v3</code>) that computed manual vector dot-products. Today, the pipeline was upgraded to the <b>official RAGAS PyPI library</b>:
    <ul>
      <li><b>Official RAGAS Metrics:</b> Direct integration of <code>faithfulness</code>, <code>context_precision</code>, <code>context_recall</code>, and <code>answer_relevancy</code> from <code>ragas.metrics</code>.</li>
      <li><b>Dedicated RAGAS Judge Model:</b> Deployed Ollama <code>mistral</code> (7B, <code>format="json"</code>, temperature 0) as the dedicated offline evaluator. This guarantees 100% clean Pydantic JSON responses, resolving previous <code>OutputParserException</code> and timeout errors from smaller models.</li>
      <li><b>Preserved Chatbot Generator:</b> Ollama <code>llama3.2</code> remains 100% untouched as your interactive RAG answer generator.</li>
      <li><b>Chunk Boundary Preservation:</b> Solr KNN search results are preserved as discrete string lists (<code>retrieved_contexts = [chunk1, chunk2, ...]</code>) matching official RAGAS expectations.</li>
      <li><b>Zero Error Masking:</b> Removed <code>fillna(0.0)</code> to ensure all reported metrics represent true LLM-as-a-judge entailment evaluation.</li>
    </ul>
    """
    elements.append(Paragraph(p1_intro, body_style))

    # Screenshot 1: Environment
    img1_path = os.path.join(SCREENSHOT_DIR, "1_environment_setup.png")
    if os.path.exists(img1_path):
        elements.append(Image(img1_path, width=460, height=255))
        elements.append(Paragraph("Figure 1: Environment & Package Verification (Official RAGAS v0.4.3, LangSmith v0.10.6, Datasets v5.0.0)", caption_style))

    elements.append(Paragraph("3.2 The 5 Test Questions & Input Transparency", h2_style))
    q_table_data = [
        [Paragraph("<b>Q#</b>", body_style), Paragraph("<b>Test Question</b>", body_style), Paragraph("<b>Reference Ground Truth Answer</b>", body_style)],
        ["Q1", "What is ChromaDB and how is it used in the project?", "ChromaDB is a vector database used to build an in-memory vector store that allows users to upload a PDF interactively and perform similarity search without requiring an external database server."],
        ["Q2", "What embedding model is used for generating dense vectors in this pipeline?", "The pipeline uses sentence-transformers/all-MiniLM-L6-v2 via LangChain's HuggingFaceEmbeddings to generate 384-dimensional dense vectors."],
        ["Q3", "How is Apache Solr queried for vector search in rag_chain.py?", "Apache Solr is queried using a k-nearest-neighbor filter {!knn f=embedding topK=5} passed via the fq parameter in pysolr to retrieve the top 5 closest chunk vectors."],
        ["Q4", "What happens if a user types a generic greeting like 'hey'?", "When a generic greeting like 'hey' is typed, Solr KNN still returns top-K nearest chunks, but since none contain an answer to 'hey', the LLM prompt instructs it to fall back to 'I couldn't find the answer in the provided document.'"],
        ["Q5", "Give some examples of incident management features in the HSE Management System.", "Examples of incident management features include creating, editing, viewing, deleting, changing status, and assigning tasks to specific individuals, as well as an incident trend chart and dashboard usage metrics."]
    ]
    t_questions = Table(q_table_data, colWidths=[30, 220, 230])
    t_questions.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(t_questions)
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("3.3 Empirical Official RAGAS Results Table", h2_style))
    res_table_data = [
        [Paragraph("<b>Q#</b>", body_style), Paragraph("<b>Faithfulness</b>", body_style), Paragraph("<b>Ctx Precision</b>", body_style), Paragraph("<b>Ctx Recall</b>", body_style), Paragraph("<b>Answer Relevancy</b>", body_style), Paragraph("<b>Mean Score</b>", body_style)],
        ["Q1", "1.000", "1.000", "0.800", "0.773", "0.893"],
        ["Q2", "1.000", "1.000", "0.000", "0.380", "0.595"],
        ["Q3", "1.000", "1.000", "1.000", "0.918", "0.979"],
        ["Q4", "1.000", "1.000", "0.000", "0.000", "0.500"],
        ["Q5", "1.000", "0.887", "1.000", "0.717", "0.901"],
        [Paragraph("<b>Overall</b>", body_style), Paragraph("<b>1.000</b>", body_style), Paragraph("<b>0.977</b>", body_style), Paragraph("<b>0.560</b>", body_style), Paragraph("<b>0.558</b>", body_style), Paragraph("<b>0.774</b>", body_style)],
    ]
    t_results = Table(res_table_data, colWidths=[40, 85, 85, 85, 95, 90])
    t_results.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2B6CB0")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#EDF2F7")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(t_results)
    elements.append(Spacer(1, 10))

    # Screenshots 2 & 3
    img2_path = os.path.join(SCREENSHOT_DIR, "2_results_table_csv.png")
    if os.path.exists(img2_path):
        elements.append(Image(img2_path, width=460, height=255))
        elements.append(Paragraph("Figure 2: Empirical RAGAS Exported Results Table (ragas_results_table.csv)", caption_style))

    img3_path = os.path.join(SCREENSHOT_DIR, "3_overall_benchmark_scores_json.png")
    if os.path.exists(img3_path):
        elements.append(Image(img3_path, width=460, height=255))
        elements.append(Paragraph("Figure 3: Overall Benchmark Summary JSON (ragas_evaluation_results.json - Overall Score: 0.774)", caption_style))

    elements.append(Paragraph("3.4 Failure Case Analysis & Production Remediation", h2_style))
    p1_failure = """
    <b>Primary Failure Case Analysis (Q4 & Q2):</b><br/>
    <ul>
      <li><b>Q4 ("What happens if a user types a generic greeting like 'hey'?"):</b> Achieved a mean score of <code>0.500</code>. Solr KNN retrieves code chunks containing fallback instructions. The LLM correctly outputs <i>"I couldn't find the answer in the provided document."</i> Faithfulness and Context Precision are 1.000 (perfect ground truth adherence). Context Recall and Answer Relevancy are 0.000 because no factual claim was requested or generated.</li>
      <li><b>Q2 ("What embedding model is used for generating dense vectors..."):</b> Achieved a mean score of <code>0.595</code>. Solr retrieved pgvector table definitions displaying <code>Column(Vector(384))</code> rather than the MiniLM model string, resulting in Context Recall = 0.000 against reference ground truth.</li>
    </ul>
    <b>Production Remediation Plan:</b>
    <ol>
      <li><b>Conversational Query Expansion:</b> Implement pre-retrieval query rewriting to expand short or ambiguous follow-up queries.</li>
      <li><b>Cross-Encoder Reranking:</b> Apply <code>ms-marco-MiniLM-L-6-v2</code> post-retrieval to re-rank Solr chunks before building LLM context prompts.</li>
    </ol>
    """
    elements.append(Paragraph(p1_failure, body_style))

    img4_path = os.path.join(SCREENSHOT_DIR, "4_failure_analysis_md.png")
    if os.path.exists(img4_path):
        elements.append(Image(img4_path, width=460, height=255))
        elements.append(Paragraph("Figure 4: Failure Case Analysis Report (failure_analysis.md)", caption_style))

    elements.append(Paragraph("3.5 LangSmith Telemetry & Trace Evidence", h2_style))
    p1_langsmith = """
    All 5 live pipeline execution traces were logged directly to LangSmith project <code>PPT-Semantic-RAG-Evaluation</code>. Each trace captured the exact execution context, latency, model parameters, and received 4 official RAGAS feedback badges (<code>faithfulness</code>, <code>context_precision</code>, <code>context_recall</code>, <code>answer_relevancy</code>) attached via <code>client.create_feedback()</code>.
    """
    elements.append(Paragraph(p1_langsmith, body_style))

    img5_path = os.path.join(SCREENSHOT_DIR, "5_langsmith_feedback_ui.png")
    if os.path.exists(img5_path):
        elements.append(Image(img5_path, width=460, height=255))
        elements.append(Paragraph("Figure 5: LangSmith Web Interface - Live Trace Feedback Badges for PPT-Semantic-RAG-Evaluation", caption_style))

    elements.append(PageBreak())

    # -------------------------------------------------------------------------
    # PART 2: LLM GUARDRAILS IMPLEMENTATION
    # -------------------------------------------------------------------------
    elements.append(Paragraph("Part 2: LLM Guardrails Implementation", h1_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E0"), spaceAfter=12))

    p2_intro = """
    <b>4.1 Framework Choice & Architecture Rationale</b><br/>
    <b>Framework Chosen:</b> <b>LangChain-Native Output Validators (<code>StrOutputParser</code> / <code>OutputParserException</code> via <code>LangChainOutputValidator</code>) combined with embedded MiniLM vector guardrails</b>.<br/>
    <b>Why Chosen:</b> Avoids heavy external framework dependencies (such as NeMo Guardrails or Guardrails AI), eliminates extra LLM latency, and seamlessly integrates into the existing LangChain execution chain while reusing sentence-transformers embeddings.
    <br/><br/>
    <b>4.2 Four Protection Categories Implemented</b>
    <ol>
      <li><b>Prompt Injection Attempts (Input Guardrail):</b> Regex pattern matching (<code>INJECTION_PATTERNS</code>) evaluated <b>ONLY on the current raw user question</b> to prevent conversation history poisoning.</li>
      <li><b>Off-Topic Queries (Input Guardrail):</b> MiniLM embedding cosine similarity evaluated against domain reference phrases (<code>OFF_TOPIC_THRESHOLD = 0.25</code>).</li>
      <li><b>Hallucinated / Unsupported Output (Output Guardrail):</b> MiniLM embedding cosine similarity evaluated between retrieved Solr context and generated LLM answer (<code>FAITHFULNESS_THRESHOLD = 0.30</code>).</li>
      <li><b>Malformed / Prompt-Leaking Output (Output Guardrail):</b> LangChain <code>LangChainOutputValidator</code> subclassing <code>StrOutputParser</code> and raising <code>OutputParserException</code> if output is empty, too short, or leaks internal prompt markers.</li>
    </ol>
    """
    elements.append(Paragraph(p2_intro, body_style))

    elements.append(Paragraph("4.3 Guardrail-Memory Integration Architecture", h2_style))
    p2_memory = """
    <b>Key Integration Fix:</b> Prompt-injection pattern matching evaluates <code>question</code> (the current raw user input), while off-topic query detection evaluates <code>context_question</code> (<code>history + question</code>). If a user message is blocked by input guardrails, <b>it is NOT added to <code>chat_history</code></b>.<br/>
    This ensures that:
    <ul>
      <li>Prompt-injection attempts do not contaminate subsequent conversation turns.</li>
      <li>Clean follow-up questions (e.g. <i>"What's the best recipe for chocolate chip cookies?"</i>) immediately after a blocked prompt injection are correctly classified as <b>OFF-TOPIC</b>, not prompt injection.</li>
      <li>Legitimate multi-turn follow-up questions (e.g. <i>"What is the incident management module?"</i> followed by <i>"What features does it have?"</i>) resolve context cleanly via conversational memory.</li>
    </ul>
    """
    elements.append(Paragraph(p2_memory, body_style))

    elements.append(Paragraph("4.4 Test Cases & Verification Evidence", h2_style))

    # Screenshots guardss, guard2, guard3
    img_ss_path = os.path.join(SCREENSHOT_DIR, "guardss.png")
    if os.path.exists(img_ss_path):
        elements.append(Image(img_ss_path, width=460, height=255))
        elements.append(Paragraph("Figure 6: Terminal Proof - Turn A (Prompt Injection Blocked) & Turn B (Off-Topic Blocked in Same Session)", caption_style))

    img_g2_path = os.path.join(SCREENSHOT_DIR, "guard2.png")
    if os.path.exists(img_g2_path):
        elements.append(Image(img_g2_path, width=460, height=255))
        elements.append(Paragraph("Figure 7: Terminal Proof - Turn C (Legitimate Query Allowed with Solr Retrieved Chunks Displayed)", caption_style))

    img_g3_path = os.path.join(SCREENSHOT_DIR, "guard3.png")
    if os.path.exists(img_g3_path):
        elements.append(Image(img_g3_path, width=460, height=255))
        elements.append(Paragraph("Figure 8: Automated Test Suite Proof (python test_guardrails.py Cases 1–5 Passing 100%)", caption_style))

    elements.append(Paragraph("4.5 Framework Limitations Found", h2_style))
    p2_limits = """
    <ul>
      <li><b>Static Regex Dependency:</b> Prompt injection detection relies on predefined regex patterns. Novel or heavily obfuscated adversarial prompts require ongoing rule updates.</li>
      <li><b>Fixed Similarity Thresholds:</b> Fixed cosine-similarity thresholds (0.25 for off-topic, 0.30 for hallucination) require tuning based on document chunk density and text length.</li>
    </ul>
    """
    elements.append(Paragraph(p2_limits, body_style))

    elements.append(PageBreak())

    # -------------------------------------------------------------------------
    # PART 3: UNABRIDGED SOURCE CODE APPENDICES
    # -------------------------------------------------------------------------
    elements.append(Paragraph("Part 3: Complete Source Code Appendices (Unabridged)", h1_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E0"), spaceAfter=12))

    code_files = [
        ("Appendix A: evaluate_ragas.py", r"C:\Users\EileneAnnaKuriakose\ppt_rag_evaluation\evaluate_ragas.py"),
        ("Appendix B: guardrails.py", r"C:\Users\EileneAnnaKuriakose\ppt_rag_evaluation\guardrails.py"),
        ("Appendix C: rag_chain.py", r"C:\Users\EileneAnnaKuriakose\ppt_rag_evaluation\rag_chain.py"),
        ("Appendix D: test_guardrails.py", r"C:\Users\EileneAnnaKuriakose\ppt_rag_evaluation\test_guardrails.py"),
        ("Appendix E: test_guardrail_memory_regression.py", r"C:\Users\EileneAnnaKuriakose\ppt_rag_evaluation\test_guardrail_memory_regression.py"),
        ("Appendix F: llm.py", r"C:\Users\EileneAnnaKuriakose\ppt_rag_evaluation\llm.py"),
        ("Appendix G: retriever.py", r"C:\Users\EileneAnnaKuriakose\ppt_rag_evaluation\retriever.py"),
        ("Appendix H: embeddings.py", r"C:\Users\EileneAnnaKuriakose\ppt_rag_evaluation\embeddings.py"),
        ("Appendix I: text_splitter.py", r"C:\Users\EileneAnnaKuriakose\ppt_rag_evaluation\text_splitter.py"),
        ("Appendix J: ppt_loader.py", r"C:\Users\EileneAnnaKuriakose\ppt_rag_evaluation\ppt_loader.py"),
        ("Appendix K: solr_store.py", r"C:\Users\EileneAnnaKuriakose\ppt_rag_evaluation\solr_store.py"),
        ("Appendix L: memory.py", r"C:\Users\EileneAnnaKuriakose\ppt_rag_evaluation\memory.py"),
        ("Appendix M: utils.py", r"C:\Users\EileneAnnaKuriakose\ppt_rag_evaluation\utils.py"),
    ]

    for title, filepath in code_files:
        elements.append(Paragraph(title, h2_style))
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                code_text = f.read()
            # Full UNABRIDGED code listing formatted cleanly for PDF
            safe_code = code_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>").replace(" ", "&nbsp;")
            elements.append(Paragraph(f"<code>{safe_code}</code>", code_style))
            elements.append(Spacer(1, 14))

    # Build Document
    doc.build(elements, canvasmaker=NumberedCanvas)
    print(f"[SUCCESS] Complete Unabridged PDF Generated successfully: {pdf_path}")

if __name__ == "__main__":
    create_pdf_report()
