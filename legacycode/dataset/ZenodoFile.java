package eu.dnetlib.lod.utils;

/**
 *
 * @author Giorgos Alexiou
 */
public class ZenodoFile {
    String fileName;
    String title;
    long size;
    long recordId;
    
    public ZenodoFile(String _fileName, String _title, long _size, long _recordId){
        this.fileName = _fileName;
        this.title = _title;
        this.size = _size;
        this.recordId = _recordId;
    }
    
    public String getDownloadLink(){
        return "https://zenodo.org/record/" + this.recordId + "/files/" + this.fileName;
    }
    
    @Override
    public String toString() {
        return fileName + " (" + title + ")";
    }
    
    public String toTooltip(){
        return "<html>size: " + round(size / 1000000.0, 2)  + " MB</html>";
    }
    
    public static double round(double value, int places) {
        if (places < 0) throw new IllegalArgumentException();
        
        long factor = (long) Math.pow(10, places);
        value = value * factor;
        long tmp = Math.round(value);
        return (double) tmp / factor;
    }

    public String getFileName() {
        return fileName;
    }

    public String getTitle() {
        return title;
    }

    public long getSize() {
        return size;
    }

    public long getRecordId() {
        return recordId;
    }
    
    
}
