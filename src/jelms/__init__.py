import json
from typing import Iterable, Any, Literal
from linkml_runtime.dumpers.dumper_root import Dumper
from linkml.generators.jsonldcontextgen import ContextGenerator
from linkml_runtime.linkml_model import SchemaDefinition
from linkml_runtime import SchemaView
from pydantic import BaseModel
from pyld import jsonld
from linkml_runtime.utils.formatutils import remove_empty_items

def obj_hook(o: Any) -> str:
    if isinstance(o, BaseModel):
        # Let Pydantic handle the basic serialization
        d = dict(o)

        # Add @id to the object
        for slot_name in self.sv.class_slots(o.__class__.__name__):
            slot = self.sv.get_slot(slot_name)
            if slot.identifier:
                d["@id"] = d[slot_name]
                del d[slot_name]
                break
        else:
            raise ValueError(f"Class {model.__class__.__name__} has no identifier, so it cannot be serialized to JSON-LD")

        # Add the @context to the object, if requested
        if self.context_mode == "per-object":
            d["@context"] = json.loads(ContextGenerator(schema=self.sv.schema).serialize())["@context"]

        return self.encode(d)

class JsonLdSerializer(json.JSONEncoder):
    def __init__(self, *args, sv: SchemaView, context_mode: Literal["per-object", "none"], **kwargs):
        self.sv = sv
        self.context_mode = context_mode
        super().__init__(*args, **kwargs)

    def default(self, o: Any) -> Any:
        if isinstance(o, BaseModel):
            # Let Pydantic handle the basic serialization
            d = dict(o)

            # Add @id to the object
            for slot_name in self.sv.class_slots(o.__class__.__name__):
                slot = self.sv.get_slot(slot_name)
                if slot.identifier:
                    d["@id"] = d[slot_name]
                    del d[slot_name]
                    break
            else:
                raise ValueError(f"Class {model.__class__.__name__} has no identifier, so it cannot be serialized to JSON-LD")

            # Add the @context to the object, if requested
            if self.context_mode == "per-object":
                d["@context"] = json.loads(ContextGenerator(schema=self.sv.schema).serialize())["@context"]

            # Add @type if the slot is an identifier
            d["@type"] = o.__class__.__name__

            return remove_empty_items(d)
        else:
            raise TypeError(f"Object of type {type(o)} is not JSON serializable")

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

def remove_id_mapping(d: Any) -> Any:
    """
    Removes any context keys that map to @id, since we want to use the @id key only
    """
    if isinstance(d, dict):
        return {k: remove_id_mapping(v) for k, v in d.items() if v != "@id"}
    elif isinstance(d, list):
        return [remove_id_mapping(v) for v in d]
    return d

class JsonLdDumper(Dumper):
    def dumps(self, element: BaseModel | Iterable[BaseModel], schema: str | SchemaDefinition, flatten: bool = False, **_) -> str:
        sv = SchemaView(schema)
        serializer = JsonLdSerializer(sv=sv, context_mode="none")
        context_generator = ContextGenerator(schema=schema)
        context = remove_id_mapping(json.loads(context_generator.serialize())["@context"])

        if isinstance(element, BaseModel):
            # model = model_to_dict(element, sv)
            # model["@context"] = context
            doc = json.loads(serializer.encode(element))
            doc["@context"] = context
        else:
            # If we are dumping multiple elements, we can use a named graph in JSON-LD
            # https://www.w3.org/TR/json-ld/#named-graphs
            doc = {
                "@graph": [e for e in element],
                "@context": context
            }
        return serializer.encode(doc)
