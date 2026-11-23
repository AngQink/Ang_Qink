import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.time.LocalDateTime;
import java.util.*;
import java.util.zip.*;

public class Main {
    private record Choice(int version, byte[] bytes) {}
    private static final String META = "META-INF/MANIFEST.MF";
    private static final String VERSIONED = "META-INF/versions/";
    private static final byte[] MANIFEST =
        "Manifest-Version: 1.0\r\nMain-Class: Greeting\r\n\r\n".getBytes(StandardCharsets.UTF_8);

    private static void emit(ZipOutputStream zip, String name, byte[] data) throws IOException {
        CRC32 crc = new CRC32();
        crc.update(data);
        ZipEntry item = new ZipEntry(name);
        item.setMethod(ZipEntry.STORED);
        item.setSize(data.length);
        item.setCompressedSize(data.length);
        item.setCrc(crc.getValue());
        item.setTimeLocal(LocalDateTime.of(1980,1,1,0,0));
        zip.putNextEntry(item);
        zip.write(data);
        zip.closeEntry();
    }

    private static void copy(Path input, Path output, int ceiling) throws IOException {
        Map<String,Choice> selected = new TreeMap<>();
        try (ZipFile archive = new ZipFile(input.toFile())) {
            for (ZipEntry entry : Collections.list(archive.entries())) {
                String name = entry.getName();
                if (entry.isDirectory() || name.equals(META)) continue;
                int version = 0;
                if (name.startsWith(VERSIONED)) {
                    int slash = name.indexOf('/', VERSIONED.length());
                    version = Integer.parseInt(name.substring(VERSIONED.length(), slash));
                    name = name.substring(slash + 1);
                    if (version > ceiling || version < 9) continue;
                }
                Choice old = selected.get(name);
                if (old == null || version > old.version()) {
                    try (InputStream in = archive.getInputStream(entry)) {
                        selected.put(name, new Choice(version, in.readAllBytes()));
                    }
                }
            }
        }
        try (ZipOutputStream zip = new ZipOutputStream(Files.newOutputStream(output))) {
            emit(zip, META, MANIFEST);
            for (var row : selected.entrySet()) emit(zip, row.getKey(), row.getValue().bytes());
        }
    }

    public static void main(String[] args) throws Exception {
        Path jobs = Path.of(args[0]).toAbsolutePath();
        for (String line : Files.readAllLines(jobs, StandardCharsets.UTF_8)) {
            String[] fields = line.split("\t", -1);
            copy(jobs.resolveSibling(fields[1]), jobs.resolveSibling(fields[2]), Integer.parseInt(fields[0]));
        }
    }
}
