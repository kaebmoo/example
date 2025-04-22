จากเอกสาร "Introducing Contextual Retrieval" https://www.anthropic.com/news/contextual-retrieval
และจากสรุปที่เราได้คุยกันไปก่อนหน้านี้ ขั้นตอนการทำงานของ **Contextual Retrieval** สามารถอธิบายเป็นภาษาไทยได้ดังนี้:

1.  **แบ่งฐานข้อมูลออกเป็นส่วนย่อยๆ (Chunks)**. ขั้นตอนแรกคือการแบ่งเอกสารทั้งหมดในฐานข้อมูลของคุณออกเป็นชิ้นส่วนข้อความขนาดเล็ก โดยทั่วไปจะไม่เกินสองสามร้อยโทเค็น.

2.  **สร้างบริบทเฉพาะสำหรับแต่ละ Chunk โดยใช้ Claude**.
    *   เอกสารจะถูกส่งไปยัง Claude พร้อมกับ Chunk ที่ต้องการสร้างบริบท.
    *   Claude จะสร้าง **บริบทที่กระชับ** (short succinct context) ที่อธิบายความสัมพันธ์ของ Chunk นั้นๆ กับเอกสารทั้งหมด. บริบทนี้มักจะมีความยาวประมาณ 50-100 โทเค็น.
    *   ตัวอย่าง prompt ที่ใช้กับ Claude คือ:
        ```
        <document> {{WHOLE_DOCUMENT}} </document> Here is the chunk we want to situate within the whole document <chunk> {{CHUNK_CONTENT}} </chunk> Please give a short succinct context to situate this chunk within the overall document for the purposes of improving search retrieval of the chunk. Answer only with the succinct context and nothing else.
        ```

3.  **เพิ่มบริบทที่สร้างขึ้นไว้ด้านหน้าของแต่ละ Chunk**. บริบทที่ได้จาก Claude จะถูกนำมาต่อ (prepend) ไว้ด้านหน้าของเนื้อหา Chunk เดิม. Chunk ที่มีบริบทนี้เรียกว่า **"contextualized_chunk"**. ตัวอย่างเช่น:
    ```
    original_chunk = "The company's revenue grew by 3% over the previous quarter."
    contextualized_chunk = "This chunk is from an SEC filing on ACME corp's performance in Q2 2023; the previous quarter's revenue was $314 million. The company's revenue grew by 3% over the previous quarter."
    ```

4.  **สร้าง Contextual Embeddings และ/หรือ Contextual BM25 Index**.
    *   นำ **contextualized chunks** จากขั้นตอนที่ 3 ไปสร้าง **vector embeddings** โดยใช้ embedding model. นี่คือ **"Contextual Embeddings"**.
    *   นอกจากนี้ ยังนำ **contextualized chunks** ไปสร้างดัชนี **BM25**. นี่คือ **"Contextual BM25"**.

5.  **ดำเนินการดึงข้อมูลเมื่อมีคำถามจากผู้ใช้**.
    *   เมื่อผู้ใช้ป้อนคำถาม ระบบจะใช้ **Contextual Embeddings** เพื่อค้นหา Chunks ที่มีความหมายใกล้เคียงกับคำถามในเชิงความหมาย (semantic similarity).
    *   และ/หรือใช้ **Contextual BM25** เพื่อค้นหา Chunks ที่มีคำหรือวลีที่ตรงกับคำถามอย่างแม่นยำ (lexical matching).

6.  **(ทางเลือก) รวมและคัดกรองผลลัพธ์**. หากใช้ทั้ง Contextual Embeddings และ Contextual BM25 ระบบจะรวมผลลัพธ์ที่ได้จากทั้งสองวิธีเข้าด้วยกันและทำการลบข้อมูลที่ซ้ำซ้อน (deduplicate) โดยใช้เทคนิคการรวมอันดับ (rank fusion).

7.  **(ทางเลือก) ทำการ Reranking**. ผลลัพธ์ที่ได้จากการดึงข้อมูลในขั้นตอนที่ 5 หรือ 6 (อาจมีจำนวนมากถึง 150 Chunks) จะถูกนำไปผ่านโมเดล **Reranking**. โมเดลนี้จะให้คะแนนแต่ละ Chunk ตามความเกี่ยวข้องและความสำคัญต่อคำถามของผู้ใช้ จากนั้นจะเลือกเฉพาะ Chunks ที่มีคะแนนสูงสุด (เช่น 20 อันดับแรก).

8.  **ส่ง Chunks ที่ได้ไปยังโมเดลภาษา**. Chunks ที่ถูกคัดเลือกมาแล้ว (จากขั้นตอนที่ 5, 6 หรือ 7) จะถูกนำไปใส่ใน prompt พร้อมกับคำถามของผู้ใช้ เพื่อให้โมเดลภาษาใช้เป็นบริบทในการสร้างคำตอบสุดท้าย.

การใช้ **prompt caching** ของ Claude สามารถช่วยลดต้นทุนในการสร้าง contextualized chunks ได้ เนื่องจากเอกสารทั้งหมดจะถูกโหลดเข้า cache เพียงครั้งเดียวเท่านั้น.

โดยสรุป ขั้นตอนหลักของ Contextual Retrieval คือการ **เพิ่มบริบทให้กับแต่ละ Chunk ก่อนทำการ embedding และสร้างดัชนี BM25** ซึ่งช่วยให้ระบบสามารถดึงข้อมูลที่เกี่ยวข้องได้อย่างแม่นยำยิ่งขึ้น. การใช้ **Reranking** ร่วมด้วยจะยิ่งช่วยเพิ่มประสิทธิภาพในการดึงข้อมูล.