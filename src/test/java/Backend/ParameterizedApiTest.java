package Backend;

import org.testng.annotations.DataProvider;
import org.testng.annotations.Test;

import static io.restassured.RestAssured.*;

public class ParameterizedApiTest 
{
	@DataProvider(name = "userIds")
    public Object[][] getUserIds() {
        return new Object[][] {
            { 1 },
            { 2 },
            { 3 }
        };
    }

    @Test(dataProvider = "userIds")
    public void getUserById(int userId) {
        given()
            .baseUri("https://reqres.in")
        .when()
            .get("/api/users/" + userId)
        .then()
            .statusCode(200);
    }
}
