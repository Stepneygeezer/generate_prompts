
import json
from string import Template
import sys
from pathlib import Path

def generate_prompts(requirements_file_path, output_file_path):
    with open(requirements_file_path, "r") as f:
        req = json.load(f)

    resource_name = req["name"]
    prompts = []

    template_map = {
        "contracts": {
            "condition": True,
            "name": "01-contracts",
            "template": Template("""Generate complete C# code files for the `${ResourceName}Document`, `${ResourceName}Collection`, and `${ResourceName}Summary` in `/src/Monolith.Crm.Contracts/Contracts/V2`.

Each file must include:
- Correct `namespace` based on the path: `Monolith.Crm.Contracts.Contracts.V2`
- All required `using` statements
- Swagger attributes:
  - `[SwaggerDefinition("${ResourceName}")]` for the document
  - `[SwaggerDefinition("${ResourceName}Summary")]` for the summary
- The collection should implement `CollectionResource<${ResourceName}Document>`
- Each file must be copy-paste ready and compile without modification.

Generate all three files in full.""")
        },
        "validation": {
            "condition": req.get("hasValidation"),
            "name": "02-validation",
            "template": Template("""Generate full C# files for:
1. `${ResourceName}.cs` — containing validation logic.
2. `${ResourceName}Constants.cs` — defining reusable constants.

Both should be placed in `/src/Monolith.Crm.Contracts/Validation` with namespace `Monolith.Crm.Contracts.Validation`.
Include `using` statements and make the files compile-ready.""")
        },
        "domain": {
            "condition": req.get("hasDomainModel"),
            "name": "03-domain-model",
            "template": Template("""Generate the domain model `${ResourceName}.cs` for `/src/Monolith.Crm/Domain`, with namespace `Monolith.Crm.Domain`.

- Include `[Audit("CRM", "T${ResourceName}", "Id", "Id")]` attribute
- Implement `EqualityAndHashCodeProvider<${ResourceName}, int>`
- Include properties such as Id, Description, Date
- Include all required `using` directives.""")
        },
        "events": {
            "condition": req.get("hasEvents"),
            "name": "04-messaging-events",
            "template": Template("""Generate two C# messaging event classes:
1. `${ResourceName}Created`
2. `${ResourceName}Changed`

Both should be in `/src/Monolith.Crm/Messaging` with namespace `Monolith.Crm.Messaging`.
- Implement `BusMessage` and `IEventMessage<${ResourceName}Document>`
- Include complete `using` statements and make the files compile-ready.""")
        },
        "controller": {
            "condition": req.get("hasController"),
            "name": "05-controller",
            "template": Template("""Generate the controller class `${ResourceName}Controller.cs` located at `/src/Monolith.Crm/v2/Controllers`, namespace `Monolith.Crm.v2.Controllers`.

- Include RESTful actions (GET, POST, PUT, DELETE)
- Return `IActionResult`
- Inject dependencies (e.g., service/resource)
- Add the following attributes:
  ```csharp
  [Tags("${resourceNameLower}s")]
  [Scope(Scopes.ClientData)]
  [Authorize(CustomPolicyNames.ClientDataOrCrm)]
  [AllowedReach(ReachClaim.System, ReachClaim.Tenant, ReachClaim.User)]
  [IntelliFlo.Platform.Security.AllowedReach(ReachClaim.System, ReachClaim.Tenant, ReachClaim.User)]
  [Produces("application/json")]
  [BadRequestOnException(typeof(ValidationException), typeof(BusinessException))]
  [NotFoundOnException(typeof(ResourceNotFoundException))]
  [Route("v2/clients/")]
  ```""")
        },
        "converter_resource": {
            "condition": req.get("hasConverter") and req.get("hasResource"),
            "name": "06-converter-resource",
            "template": Template("""Generate two classes:
1. `${ResourceName}Converter.cs` in `/src/Monolith.Crm/v2/Converters/Implementation`, namespace `Monolith.Crm.v2.Converters.Implementation`
2. `${ResourceName}Resource.cs` in `/src/Monolith.Crm/v2/Resources`, namespace `Monolith.Crm.v2.Resources`

- Implement `I${ResourceName}Converter` and `I${ResourceName}Resource`
- Use dependency injection
- Include complete `using` statements.""")
        },
        "query_lang": {
            "condition": req.get("hasQueryLang"),
            "name": "07-query-language",
            "template": Template("""Generate `${ResourceName}QueryLang.cs` in `/src/Monolith.Crm/v2/Resources/QueryLang`, namespace `Monolith.Crm.v2.Resources.QueryLang`.
- Implement `I${ResourceName}QueryLang`
- Add filtering or sorting logic
- Ensure the file is copy-paste ready and compile-safe.""")
        },
        "tests": {
            "condition": req.get("hasTests"),
            "name": "08-tests",
            "template": Template("""Generate test classes for the `${ResourceName}` resource:

1. `Controllers/${ResourceName}ControllerTests.cs`
2. `Resources/${ResourceName}ResourceTests.cs`
3. `Resources/Converters/${ResourceName}ConverterTests.cs` with `[TestFixture, TestOf(typeof(${ResourceName}))]`
4. `Resources/QueryLang/${ResourceName}QueryLangTest.cs`

- Use NUnit conventions
- Include `using` statements
- Make them compile-ready.""")
        },
        "autofac": {
            "condition": req.get("hasAutofacModuleRegistration"),
            "name": "09-autofac-registration",
            "template": Template("""Update `CrmV2AutofacModule.cs` in `/src/Monolith.Crm/Modules`, namespace `Monolith.Crm.Modules`, to register `${ResourceName}` services:
- Register `I${ResourceName}Converter`, `I${ResourceName}Resource`, `I${ResourceName}QueryLang`
- Use Autofac builder pattern: `builder.RegisterType<>().As<>()`.""")
        }
    }

    for key, config in template_map.items():
        if config["condition"]:
            prompt = config["template"].substitute(
                ResourceName=req["name"],
                resourceNameLower=req["name"].lower()
            )
            prompts.append({
                "name": config["name"],
                "prompt": prompt,
                "model": "deepseek-r1",
                "stream": False
            })

    with open(output_file_path, "w") as f:
        json.dump(prompts, f, indent=2)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_prompts.py <requirements.json> <output_prompts.json>")
    else:
        generate_prompts(sys.argv[1], sys.argv[2])
        print(f"✅ Prompts generated at {sys.argv[2]}")
