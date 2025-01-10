from jelms import JsonLdDumper
from person import Person
from rdflib import Graph, Literal
from rdflib.namespace import Namespace, RDF

SCHEMA = Namespace("http://schema.org/")
EXAMPLE = Namespace("http://example.org/")


def test_unrelated_people():
    dumper = JsonLdDumper()
    raw = dumper.dumps([
        Person(name="First Person", id="http://example.org/first-person"),
        Person(name="Second Person", id="http://example.org/second-person"),
    ], schema="test/test_schema.yaml")

    # Check that it's not only valid RDF, but that the relationships are correct
    graph = Graph()
    graph.parse(data=raw, format="json-ld")
    assert list(graph.objects(subject=EXAMPLE["first-person"], predicate=SCHEMA.name)) == [Literal("First Person")]
    assert list(graph.objects(subject=EXAMPLE["first-person"], predicate=RDF.type)) == [SCHEMA["Person"]]
    assert list(graph.objects(subject=EXAMPLE["second-person"], predicate=SCHEMA.name)) == [Literal("Second Person")]
    assert list(graph.objects(subject=EXAMPLE["second-person"], predicate=RDF.type)) == [SCHEMA["Person"]]

def test_related_people():
    dumper = JsonLdDumper()
    raw = dumper.dumps(Person(
        name="First Person",
        id="http://example.org/first-person",
        knows=Person(
            name="Second Person",
            id="http://example.org/second-person"),
        ),
        schema="test/test_schema.yaml"
    )

    # Check that it's not only valid RDF, but that the relationships are correct
    graph = Graph()
    graph.parse(data=raw, format="json-ld")
    assert list(graph.objects(subject=EXAMPLE["first-person"], predicate=SCHEMA.name)) == [Literal("First Person")]
    assert list(graph.objects(subject=EXAMPLE["first-person"], predicate=RDF.type)) == [SCHEMA["Person"]]
    assert list(graph.objects(subject=EXAMPLE["first-person"], predicate=SCHEMA.knows)) == [EXAMPLE["second-person"]]
    assert list(graph.objects(subject=EXAMPLE["second-person"], predicate=SCHEMA.name)) == [Literal("Second Person")]
    assert list(graph.objects(subject=EXAMPLE["second-person"], predicate=RDF.type)) == [SCHEMA["Person"]]
