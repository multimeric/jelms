import json
from typing import Iterable
from linkml_runtime.dumpers.dumper_root import Dumper
from linkml.generators.jsonldcontextgen import ContextGenerator
from linkml_runtime.linkml_model import SchemaDefinition
from linkml_runtime import SchemaView
from pydantic import BaseModel
from pyld import jsonld
from linkml_runtime.utils.formatutils import remove_empty_items

def model_to_dict(model: BaseModel, sv: SchemaView) -> dict:
    ret = model.dict()
    # Add @id if the slot is an identifier
    for slot_name in sv.class_slots(model.__class__.__name__):
        slot = sv.get_slot(slot_name)
        if slot.identifier:
            ret["@id"] = ret[slot_name]
            del ret[slot_name]
            break
    else:
        raise ValueError(f"Class {model.__class__.__name__} has no identifier, so it cannot be serialized to JSON-LD")
    
    # Add @type if the slot is an identifier
    ret["@type"] = model.__class__.__name__
    return remove_empty_items(ret)

class JsonLdDumper(Dumper):
    def dumps(self, element: BaseModel | Iterable[BaseModel], schema: str | SchemaDefinition, flatten: bool = False, **_) -> str:
        sv = SchemaView(schema)
        context_generator = ContextGenerator(schema=schema)

        if isinstance(element, BaseModel):
            return json.dumps(model_to_dict(element, sv))
        else:
            # If we are dumping multiple elements, we can use a named graph in JSON-LD
            # https://www.w3.org/TR/json-ld/#named-graphs
            graph = {
                "@graph": [model_to_dict(e, sv) for e in element],
                "@context": json.loads(context_generator.serialize())["@context"]
            }
            if flatten:
                graph = jsonld.flatten(graph)
            return json.dumps(graph)
