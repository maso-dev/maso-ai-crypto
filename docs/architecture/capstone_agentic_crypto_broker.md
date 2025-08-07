
-----

# **Capstone Project Proposal: The Agentic Crypto Broker**

A personalized, AI-powered agent that provides actionable intelligence to help retail investors navigate the complex crypto market.

## **1. Project Specification**

### **The Business Problem: Overcoming Information Overload**

The cryptocurrency market is notoriously volatile and operates 24/7. Retail investors face significant challenges that lead to suboptimal returns. Studies on investor behavior, like DALBAR's Quantitative Analysis of Investor Behavior, consistently show that the average investor underperforms market benchmarks due to emotionally-driven decisions. This "behavior gap" can cost investors several percentage points in annual returns. The primary problems are:

  * **Information Overload:** An endless stream of news, social media chatter, and technical data makes it impossible to keep up.
  * **Emotional Decision-Making:** Market volatility often leads to fear-based selling (FUD) or greed-based buying (FOMO), resulting in poor investment outcomes.
  * **Lack of Personalization:** Generic market analysis doesn't account for an individual's specific portfolio, risk tolerance, or cost basis.

This project aims to solve this by creating an AI agent that filters the noise, provides data-driven insights, and delivers personalized, actionable recommendations.

-----

### **The Solution: An AI-Powered Personal Crypto Broker Agent**

This project will build an end-to-end agentic system that provides a highly personalized experience by integrating directly with the user's data.

**Personalization Engine:**
The agent's key value is its deep personalization. Instead of generic advice, it connects to the user's Binance account (via a read-only API key) to analyze their **actual trade history**. This allows the agent to calculate the user's average **cost basis** and real-time **Return on Investment (ROI)** for each asset. All recommendations are then framed within this personal context (e.g., "Sell BTC because its RSI is high *and your personal ROI is +45%*").

-----

### **System & AI Agent Design Diagram**

The system is designed with a decoupled architecture, separating the heavy data processing from the lightweight user-facing application. The **Frontend UI** will be structured using the **MCP (Model-Controller-Presenter)** pattern for clean separation of concerns.

```mermaid
graph TD
    subgraph Backend: Vercel Cron Job (Runs 4x/day)
        A[NewsAPI] --> C{LangChain Pipeline};
        B[Web Search] --> C;
        C -- "1. Collect & Filter" --> D["2. Enrich (Categorize, Sentiment)"];
        D -- "3. Chunk & Vectorize" --> E["4. Store in Hybrid DB"];
        E --> F[Milvus: For Vector Search];
        E --> G[Neo4j: For Graph Relationships];
    end

    subgraph Frontend: Vercel App
        H[User] --> I[Web UI (View)];
        I -- "User Actions" --> J{Agent Logic (Presenter)};
        J -- "Calls" --> M[Data Services (Model)];
        M -- "Fetches portfolio" --> K[Binance API];
        M -- "Fetches insights" --> F;
        M -- "Fetches insights" --> G;
        J -- "Processes data for UI" --> I;
        J -- "Gets summary" --> L[LLM for Summary];
        L -- "Generates recommendation" --> J;
    end

```

-----

### **UI Mockup Visuals**

To offer a clearer concept of the user interface, here is a text-based layout of the main dashboard:

```
/----------------------------------------------------------------------\
| 🤖 Agentic Crypto Broker                                             |
|----------------------------------------------------------------------|
|                                                                      |
|  PORTFOLIO OVERVIEW                                                  |
|  Total Value: $12,540.50 (+3.2% 24h)     [Chart showing 24h trend]   |
|                                                                      |
|  ========================= AGENT'S BRIEFING =========================  |
|  Good morning. Your portfolio is up 3.2% today, led by a 7% gain     |
|  in Ethereum. The market sentiment for ETH is positive due to news   |
|  about the upcoming Dencun upgrade. My recommendation is to **HOLD** |
|  your current ETH position. I've identified a rebalancing            |
|  opportunity to sell 0.01 BTC to lock in profits and increase        |
|  your USDC holdings.                                                 |
|  [Execute Rebalance] [Dismiss]                                       |
|  ====================================================================  |
|                                                                      |
|  YOUR ASSETS                                                         |
|  --------------------------------------------------------------------  |
|  Bitcoin (BTC)    Holdings: 0.25      ROI: +45.2%      [Details]     |
|  Ethereum (ETH)   Holdings: 3.50      ROI: +15.8%      [Details]     |
|  Solana (SOL)     Holdings: 50.0      ROI: -8.1%       [Details]     |
|                                                                      |
\----------------------------------------------------------------------/
```

-----

## **2. Project Write-Up**

### **Purpose & Expected Outputs**

  * **Purpose:** To empower retail crypto investors with a personalized AI tool that provides the clarity and data-driven confidence needed to make smarter investment decisions.
  * **Expected Outputs:**
    1.  A deployed web application with a live URL.
    2.  A backend service that automatically processes and analyzes crypto news.
    3.  A user interface that connects to a user's read-only Binance API key to display portfolio performance and AI-generated recommendations.

-----

### **Success Metrics**

The project's success will be evaluated based on the following metrics:

1.  **Quantitative Metric:** The performance of the "What-If Portfolio" (a future enhancement) will be tracked against a benchmark (e.g., a simple "hold BTC" strategy). Success is defined as the agent's portfolio outperforming the benchmark over a 3-month period.
2.  **Qualitative Metric:** User feedback will be collected on the clarity, relevance, and actionability of the agent's recommendations. A success rating of \>80% satisfaction will be targeted.
3.  **Technical Metric:** The RAG system's retrieval precision and generation faithfulness scores must be above 90% based on manual evaluation.

-----

### **Technology Choices & Justifications**

| Technology           | Purpose                    | Justification                                                                                                                                                                                                                           |
| :------------------- | :------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Vercel** | Hosting & Cron Jobs        | Excellent for deploying serverless functions and hosting Next.js frontends. The cron job feature is perfect for our scheduled backend service.                                                                                                |
| **Python / LangChain** | Backend Pipeline           | Python is the standard for AI/ML. LangChain provides the essential framework for orchestrating our complex data ingestion and RAG pipeline.                                                                                               |
| **Binance API** | Real-Time Portfolio Data   | Provides direct, secure (read-only) access to the user's actual portfolio balances and trade history, enabling true personalization.                                                                                                        |
| **NewsAPI / Web Search** | Data Ingestion             | NewsAPI provides a structured source of global news. Web search will supplement this to find more niche, breaking information.                                                                                                              |
| **Milvus & Neo4j** | Hybrid Graph RAG Database  | This is a standout technical choice. **Milvus** stores vector embeddings for semantic search ("What is the sentiment?"). **Neo4j** stores a knowledge graph for relationship analysis ("How is the SEC related to Binance?"). Combining them allows for far more sophisticated queries. |
| **React / Next.js** | Frontend UI                | A modern, high-performance framework for building a professional and responsive user interface.                                                                                                                                             |
| **MCP Pattern** | Frontend Architecture      | The **Model-Controller-Presenter** pattern will be used to structure the frontend code. This separates data logic (Model), application logic (Presenter), and rendering (View), making the UI easier to test, maintain, and scale. |

#### **Considered Alternatives**

  * **Hosting:** AWS EC2 was considered but rejected in favor of Vercel's serverless model, which eliminates infrastructure management and offers better cost-efficiency for a fluctuating-load application.
  * **Vector DB:** A simple `pgvector` in Postgres was considered. However, the combination of a dedicated vector DB (Milvus) and Graph DB (Neo4j) was chosen to implement a more powerful, state-of-the-art Hybrid RAG system that is a core feature of this project.

-----

### **Project Roadmap & Potential Challenges**

#### **Project Roadmap**

  * **Step 1: Foundation & API Connectivity.** Set up the project, connect to Binance API to read portfolio data.
  * **Step 2: Backend Data Ingestion.** Build the pipeline to fetch news from NewsAPI, perform quality checks, and enrich the data (categorization, sentiment).
  * **Step 3: RAG Implementation.** Set up the Milvus and Neo4j databases. Implement the logic to chunk, vectorize, and store the enriched data in our hybrid database.
  * **Step 4: Agent & Frontend Development.** Develop the core agent logic that queries the RAG system and the Binance API. Build the UI components following the MCP architecture.
  * **Step 5: Deployment & Integration Testing.** Deploy the services to Vercel, conduct end-to-end testing, and refine the agent's prompts.

#### **Potential Challenges & Mitigation Strategies**

  * **Challenge:** Managing API rate limits from NewsAPI and Binance.
      * **Mitigation:** Implement intelligent caching for data that isn't time-sensitive. Use exponential backoff for API retries. Schedule cron jobs during off-peak hours where possible.
  * **Challenge:** Ensuring high data quality from diverse web sources.
      * **Mitigation:** In addition to the blocklist and content analysis, a cross-referencing step will be implemented. A news story will be given a higher "trust score" if multiple reliable sources report it.

#### **Scalability and Bottleneck Considerations**

The serverless nature of Vercel allows the frontend and cron jobs to scale automatically with demand. The primary bottlenecks during high-traffic market events would be:

1.  **External API Limits:** The number of users we can serve simultaneously is ultimately limited by the rate limits of the Binance and NewsAPI services.
2.  **LLM Processing Time:** The generation of the final summary is a potential latency point.
    Mitigation will involve optimizing queries to fetch only essential data and exploring smaller, faster LLMs for the final summarization task if needed.

-----

### **Possible Future Enhancements**

  * **What-If Portfolio Simulator:** A stretch goal to create a "fantasy portfolio" where users can test the agent's recommendations without risking real capital.
      * **Technical Challenges:** Accurately modeling transaction fees, market slippage, and order book depth to make the simulation realistic.
  * **Multi-Exchange Support:** Integrate other exchanges like Coinbase or Nexo.
      * **Technical Challenges:** Creating an abstraction layer to normalize the data from different exchange APIs, as each has a unique structure and set of capabilities.

-----

## **3. Data Processing & RAG Implementation**

### **Data Sources & Quality Checks**

1.  **NewsAPI (News Articles)**

      * **Check 1 (Source Filtering):** A blocklist of known low-quality or biased domains will be maintained. Articles from these sources will be discarded immediately.
      * **Check 2 (Content Analysis):** A pre-processing step will check for "clickbait" language in titles and discard articles with a body text of less than 150 words to avoid stubs or low-value content.

2.  **Binance API (Market Data)**

      * **Check 1 (Price Sanity Check):** When fetching price data, ensure the value is not zero or an extreme outlier (e.g., +/- 50%) compared to the last known price to protect against API glitches.
      * **Check 2 (Liquidity Check):** The 24-hour trading volume for a given pair must be above a certain threshold to be considered for analysis, ensuring recommendations are for liquid assets.

-----

### **The RAG Architecture: Hybrid Graph RAG**

Our RAG model will use a hybrid approach to provide superior context. We will load **over 1000** unique news articles/documents, chunked into many more embeddings.

  * **Vector DB (Milvus):** Stores text embeddings for fast semantic search. Answers questions like, *"What are the most relevant recent articles about Ethereum's scalability?"*
  * **Graph DB (Neo4j):** Stores named entities (e.g., "SEC", "Coinbase", "Grayscale") and their relationships (e.g., `(SEC)-[:SUED]->(Coinbase)`). This answers questions like, *"How have regulatory actions by the SEC impacted institutional players?"*

We will also implement **re-ranking** (e.g., using Cohere's re-ranker) on the retrieved documents to ensure the top 5 most relevant chunks are passed to the LLM.

-----

### **RAG Protection & Testing**

  * **Abuse Protection:**

    1.  **Rate Limiting:** The public-facing API endpoint will be rate-limited to prevent denial-of-service attacks.
    2.  **Input Complexity Analysis:** A pre-processing step will reject user queries that are excessively long or computationally complex to prevent resource exhaustion attacks.

  * **RAG Quality Metrics & Testing:**

      * **Metrics:** We will measure **Retrieval Precision** (Are the retrieved documents relevant to the query?) and **Generation Faithfulness** (Does the final summary accurately reflect the retrieved documents without hallucination?).
      * **Integration Testing:** The RAG system will be tested with at least 5 distinct queries:
        1.  Simple fact retrieval: "What is the latest news about the Bitcoin halving?"
        2.  Sentiment analysis: "What is the current market sentiment for Solana?"
        3.  Multi-hop graph query: "Which DeFi protocols have been affected by recent security exploits?"
        4.  Comparative analysis: "Compare the recent news for Cardano vs. Polkadot."
        5.  Future-looking query: "Based on recent news, what are the biggest upcoming catalysts for the crypto market?"

-----

## **4. Deployment & Scoping**

### **Live Deployment**

The final application will be deployed on Vercel, and a live URL will be provided for evaluation. The backend cron job will be configured to refresh the knowledge base 4 times per day. Due to the costs associated with API calls, initial user access during the POC phase may be limited to a select group of beta testers, though the site itself will be public.

-----

### **Project Scope & Real-World Value**

This project addresses a **real, non-trivial use case** for retail investors. By providing an end-to-end solution—from automated data collection to a personalized user interface—it moves beyond a simple chatbot or data aggregator. It delivers tangible business value by equipping users with a tool to potentially improve their investment returns and reduce risk.

-----

## **5. Stand-Out Features**

This project is designed to excel by incorporating multiple advanced features:

  * **Technical Complexity:** The **Hybrid Graph RAG** architecture is significantly more complex and powerful than a standard vector-only RAG.
  * **Real-Time Data:** The system integrates **live, personalized portfolio data** from the Binance API, making the output directly relevant to the user.
  * **Analytics Layer:** The portfolio analysis (ROI calculation, performance tracking) serves as a critical analytics layer that scores the user's investment performance.
  * **Personalized Experience:** The entire output is tailored to the user's specific financial situation via **user authentication** (through read-only API keys).
  * **Advanced Analytical Patterns:** The agent combines time-series data (prices), unstructured data (news), and graph data (relationships) to form its recommendations.
  * **Good UI:** A clean, professional, and intuitive user interface will be built to ensure the powerful backend is accessible and easy to use.
