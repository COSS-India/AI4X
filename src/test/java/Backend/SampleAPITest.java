package Backend;

import org.testng.annotations.Test;
import static io.restassured.http.ContentType.JSON;

import static io.restassured.RestAssured.*;
import static org.hamcrest.Matchers.*;

public class SampleAPITest 
{
    @Test
    public void simpleGetTest() 
    {
        given()
            .baseUri("https://reqres.in")
        .when()
            .get("/api/users/2")
        .then()
            .statusCode(200)
            .body("data.first_name", equalTo("Janet"));
    }
    
    @Test
    public void createUser() 
    {
        given()
            .baseUri("https://reqres.in")
            .header("Content-Type", "application/json")
            .body("{ \"name\": \"morpheus\", \"job\": \"leader\" }")
        .when()
            .post("/api/users")
        .then()
            .statusCode(201)
            .body("name", equalTo("morpheus"))
            .body("job", equalTo("leader"));
    }
    
    @Test
    public void saveTemplate() {
        String payload = "{"
                + "\"floatArray\": \"\","
                + "\"img\": \"BwMDAQgBAAD//////////xsJxqRhfUJTpznaS90YJYgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACTDsNElvAQRQAAlkQAAJZEAK/ovoL9fz8BAAAAAOCiRAAA90QAgOJEAADyRACAwkQA4A5FAGCrRABAHkUAQNtEAOAdRQCgw0QAoDZFuAsAAKAPAABvAAAAPQAAAIwBAAAAAAAAAAAAAHt9AEcNChoKAOBuKm8AALT0/GjFbwAAAAAwTCpvAAC0YAEHAU4A3DwADgCDbwAAtIC6hMlvAAC0c3lzdGUDAAAAEucT0fT+PwD+7lA9vQAfEA8P8QEFEATBPuHuH87x7J7/RuAAEf0i/dEU/C/gEOBPH3zxwq0SA/3QIeEeAdIv8SKwJPACzE5S8+ROsOQfC0HzwcAz4S7+LPER4g/jTszRDwMdMl8QOxwACawlLk2+IQXDABEQ4h88NeQQ0vALz0DtPj0gER8i3yINMTDuMw4R8gMhAPAS8F4t4hIAMxn8/i7G/l0x1GMkwAIg8fKzLg7yzGASE/8MLywfEx8S0OLv4D6jIAYv0ZAglZEOEhHgbM4f7jHlEO4iYBHvMNxPwiYWDE5S3P3QYfMSX+LB//P+8ADx5v+zFAAkBA30P38QNBEQIzYRtPorAC7d8z0BPjbs+9QB4BY98tT01BPU//LeCQsj3wAfIQ8szM0WISLxsRsPDvYPH03i4jEAQc40A/LRqfCSFAMRQAoNISM00fHUQxYxIFtC4xbv/+UQE/0y709fEUNA7DHiTrJgP/AyMzwR/tILP+vR3w4iwP0fDCUPEM65wwAAAAA=\","
                + "\"referenceNumber\": \"5678790747\""
                + "}";

        given()
        	.relaxedHTTPSValidation()
            .baseUri("https://ai.mosip.sandbox.stataware.com")
            .contentType(JSON)
            .header("apikey", "95bW5t13453paJaPQE")
            .body(payload)
            .log().all()
        .when()
            .post("/qa/uat/v1/coreeid/savetemplate")
        .then()
            .statusCode(200)
            .log().all();
    }
}
