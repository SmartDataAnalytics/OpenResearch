package eu.dnetlib.lod.utils;

import java.io.BufferedInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.HashMap;
import java.util.Map;

import javax.ws.rs.Consumes;
import javax.ws.rs.PUT;
import javax.ws.rs.core.MediaType;

import org.apache.log4j.Logger;
import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

/* 
 * Copyright (C) 2015 "IMIS-Athena R.C.",
 * Institute for the Management of Information Systems, part of the "Athena" 
 * Research and Innovation Centre in Information, Communication and Knowledge Technologies.
 * [http://www.imis.athena-innovation.gr/]
 * 
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 */

import com.sun.jersey.api.client.Client;
import com.sun.jersey.api.client.ClientHandlerException;
import com.sun.jersey.api.client.ClientResponse;
import com.sun.jersey.api.client.UniformInterfaceException;
import com.sun.jersey.api.client.WebResource;
import com.sun.jersey.multipart.FormDataMultiPart;
import com.sun.jersey.multipart.file.StreamDataBodyPart;

/**
 * Class executing Zenodo Rest calls
 * @author Giorgos Alexiou
 */
public class ZenodoConnection {
    static String errorMessage = "";
    private static Logger log = Logger.getLogger(ZenodoConnection.class);
    /**
     * Verifies access token given
     * @param accessToken access token to be verified
     * @return 
     */
    public static boolean verifyAccessToken(String accessToken){
        String query = "https://zenodo.org/api/deposit/depositions/?access_token=" + accessToken;
//        System.out.println(query);

        Client client = Client.create();
        
        WebResource webResource = client.resource(query);
        ClientResponse response = webResource.accept("application/json")
                .get(ClientResponse.class);
        
        if (response.getStatus() != 200) {
            
            return false;
            
        }
        return true;
    }
    
    /**
     * Lists deposition files
     * @param accessToken
     * @return a map containing an increasing id for key and a file in value
     */
    public static Map<Integer, ZenodoFile> getDepositionFiles(String accessToken){
        Map<Integer, ZenodoFile> files = new HashMap<>();
        String query = "https://zenodo.org/api/deposit/depositions/?access_token=" + accessToken;
//        System.out.println(query);
        try {
            
            Client client = Client.create();
            
            WebResource webResource = client.resource(query);
            ClientResponse response = webResource.accept("application/json")
                    .get(ClientResponse.class);
            
            if (response.getStatus() != 200) {
                errorMessage = ("Connection to Zenodo failed\n(error code: "
                        + response.getStatus() + ")");
                
                return null;
                
            }
            
            //parsing response from zenodo
            JSONParser parser = new JSONParser();
            
            JSONArray objArray = (JSONArray)parser.parse(response.getEntity(String.class));
            
            int fileNumb = 0;
            
            //parsing files
            for(Object obj : objArray){
                JSONObject depositionJson = (JSONObject)obj;
                
                //deposition details
                String title = (String)depositionJson.get("title");
                Long recordId = (Long)depositionJson.get("record_id");
                
                //bypass Unsubmitted files
                if(recordId == null)
                    continue;
                
                //deposition files details
                JSONArray filesArray = (JSONArray)depositionJson.get("files");
                for(Object fileObj : filesArray){
                    JSONObject fileJson = (JSONObject)fileObj;
                    String filename = (String)fileJson.get("filename");
                    long size = Long.parseLong((String)fileJson.get("filesize"));
                    
                    ZenodoFile file = new ZenodoFile(filename, title, size, recordId);
//                    System.out.println(file);
                    files.put(fileNumb, file);
                    fileNumb++;
                }
            }
        } catch (UniformInterfaceException | ClientHandlerException e) {
            errorMessage = "An error occurred connecting of Zenodo";
            return null;
        } catch (ParseException ex) {
            errorMessage = "An error occurred parsing data from Zenodo";
            return null;
        }
        
        return files;
    }
    
    public static String getErrorMessage(){
        return errorMessage;
    }
    
    /**
     * Donwloads a file from Zenodo to the filesystem
     * @param file file from Zenodo to download
     * @param filename path to store downloaded file
     * @throws MalformedURLException
     * @throws IOException 
     */
    public static void downloadFile(ZenodoFile file, final String filename)
            throws MalformedURLException, IOException {
        String urlString = file.getDownloadLink();
        
        BufferedInputStream in = null;
        FileOutputStream fout = null;
        try {
            in = new BufferedInputStream(new URL(urlString).openStream());
            fout = new FileOutputStream(filename);
            
            final byte data[] = new byte[1024];
            int count;
            while ((count = in.read(data, 0, 1024)) != -1) {
                fout.write(data, 0, count);
            }
        } finally {
            if (in != null) {
                in.close();
            }
            if (fout != null) {
                fout.close();
            }
        }
    }
    
    /**
     * Creates a Zenodo deposition
     * @param accessToken 
     * @param title 
     * @param type 
     * @param description 
     * @param author
     * @param affiliation
     * @param access
     * @return newly created deposition's id
     */
    public static Long createDeposition(String accessToken,
            String title, String type, String description,
            String author, String affiliation, String access){
        
        //create json object with arguments
        JSONObject metadataJson = new JSONObject();
        metadataJson.put("title", title);
        metadataJson.put("upload_type", type);
        metadataJson.put("description", description);
        
        
        JSONObject creator = new JSONObject();
        creator.put("name", author);
        creator.put("affiliation", affiliation);
        
        JSONArray creators = new JSONArray();
        creators.add(creator);
        metadataJson.put("creators", creators);
//        metadataJson.put("access_right", access);
        
        JSONObject obj = new JSONObject();
        obj.put("metadata", metadataJson);
        
        System.err.println(obj.toJSONString());
//        System.out.println(obj.toJSONString());
        
        Client client = Client.create();
        
        //execute post call
        WebResource webResource = client
                .resource("https://zenodo.org/api/deposit/depositions/?access_token="+accessToken);
        
        ClientResponse response = webResource.type("application/json")
                .post(ClientResponse.class, obj.toJSONString());
        
        if (response.getStatus() != 201) {
            errorMessage = ("Connection to Zenodo failed\n(error code: "
                    + response.getStatus() + ")");
            System.err.println(errorMessage);
            return null;
        }
        
        //parse response to get deposition id
        JSONParser parser = new JSONParser();
        JSONObject responseJson;
        try {
            responseJson = (JSONObject)parser.parse(response.getEntity(String.class));
        } catch (ParseException ex) {
            errorMessage = "An error occurred parsing data from Zenodo";
            return null;
        }
        
        Long depositionId = (Long)responseJson.get(("id"));
//        System.out.println("Created deposition with id : " + depositionId);
        return depositionId;
    }
    
    /**
     * Adds a new file to a Zenodo deposition
     * @param depositionId
     * @param file
     * @param filename
     * @param accessToken
     * @return true if file added successfully, false otherwise
     * @throws IOException 
     */
//    public static boolean uploadFileToDeposition(Long depositionId, String file, String filename, String accessToken){
    @PUT
    @Consumes("application/octet-stream")
    public static boolean uploadFileToDeposition(Long depositionId, BufferedInputStream bufferedInStream, String filename, String accessToken) throws IOException{
        Client client = Client.create();
        
        WebResource resource = client
                .resource("https://zenodo.org/api/deposit/depositions/" + depositionId + "/files?access_token=" + accessToken);
        final FormDataMultiPart formDataMultiPart = new FormDataMultiPart();
        
//        InputStream fileInStream = new FileInputStream(file);
//        BufferedInputStream bufferedInStream =  new BufferedInputStream(fileInStream);
        
        formDataMultiPart.field("filename", filename);
        
//        FileDataBodyPart fdp = new  FileDataBodyPart("file",
//               file, //new File(file),
//                MediaType.APPLICATION_OCTET_STREAM_TYPE);
        
        StreamDataBodyPart sdbp = new StreamDataBodyPart("file", bufferedInStream,MediaType.APPLICATION_OCTET_STREAM);
        
        
        formDataMultiPart.bodyPart(sdbp);
        
        ClientResponse response = resource.type(MediaType.MULTIPART_FORM_DATA)
                .accept(MediaType.TEXT_HTML)
                .post(ClientResponse.class, formDataMultiPart);
        
        if (response.getStatus() != 201) {
            errorMessage = "Error uploading file to Zenodo";
            log.error(errorMessage+"  status: "+response.getStatus());
            return false;
        }
        
        sdbp.cleanup();
        formDataMultiPart.cleanup();
        formDataMultiPart.close();
        bufferedInStream.close();
        System.out.println("File uploaded");
        return true;
    }
    
    /**
     * Publishes a Zenodo deposition
     * @param depositionId
     * @param accessToken
     * @return true if deposition was published successfully, false otherwise
     */
    public static String publishDeposition(Long depositionId, String accessToken){
        Client client = Client.create();
        
        WebResource resource = client
                .resource("https://zenodo.org/api/deposit/depositions/" + depositionId + "/actions/publish?access_token=" + accessToken);
        ClientResponse response = resource.post(ClientResponse.class);
        if (response.getStatus() != 202) {
            errorMessage = "Error publishing file to Zenodo";
            return null;
        }
        
        //parse response to get deposition id
        JSONParser parser = new JSONParser();
        JSONObject responseJson;
        try {
            responseJson = (JSONObject)parser.parse(response.getEntity(String.class));
        } catch (ParseException ex) {
            errorMessage = "An error occurred parsing data from Zenodo";
            return null;
        }
        
        String doiURL = (String)responseJson.get(("doi_url"));
        
		System.out.println("deposition published");
        return doiURL;
    }
}
