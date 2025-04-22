// ตัวอย่างการใช้ Apache Tika ใน Java
package TextExtractor; // ต้องระบุ package ให้ตรงกับโฟลเดอร์

import org.apache.tika.Tika;
import org.apache.tika.exception.TikaException;
import java.io.File;
import java.io.IOException;

public class App {
    public static void main(String[] args) throws IOException, TikaException {
        Tika tika = new Tika();
        File file = new File("/Users/seal/Downloads/pil_Acetylcysteine (GRANULES).pdf"); // หรือ .docx .pdf
        String content = tika.parseToString(file);
        System.out.println(content);
    }
}
