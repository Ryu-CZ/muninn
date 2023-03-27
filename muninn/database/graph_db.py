from neo4j import GraphDatabase


class GraphDB:
    """
    Knowledge unit nodes types:

    Entity: Represents an entity in the text, which can be a subject, object, or any other type of entity. This
        node can have properties like text (the textual content of the entity).
    Predicate: Represents the predicate of a sentence. This node can have properties like text (the textual content
        of the predicate).
    Fact: Represents a fact from the original text. This node can have properties like text (the
        textual content of the fact) and embedding (the corresponding embedding).
    Record: Represents a series of facts that belong to a single message or context. This node can have properties like
        text (the textual content of the record).

    Knowledge unit nodes relationships:

    NEXT: Connects two Fact nodes, indicating the order of facts within the text.
    PART_OF: Connects an Entity or Predicate to a Fact node, indicating that the entity or
        predicate is a part of the fact.
    CONTAINS: Connects a Record node to one or more Fact nodes, indicating that the facts are part of the record.
    AUTHOR: Connects a Record node to an Entity node, indicating that the entity is the author of the record.


    Here's an example of how the updated knowledge unit format might be represented in a graph:

    Text: "John bought a book. He gave it to Mary."

    Graph representation:

    Nodes:
        Entity1: {text: "John"},
        Entity2: {text: "a book"},
        Entity3: {text: "He"},
        Entity4: {text: "it"},
        Entity5: {text: "Mary"},
        Predicate1: {text: "bought"},
        Predicate2: {text: "gave"},
        Fact1: {text: "John bought a book", embedding: [...]},
        Fact2: {text: "He gave it to Mary", embedding: [...]},
        Record1: {text: "John bought a book. He gave it to Mary."},
    Relationships:
        Fact1 -[NEXT]-> Fact2,
        Entity1 -[PART_OF {role: "subject"}]-> Fact1,
        Entity2 -[PART_OF {role: "object"}]-> Fact1,
        Predicate1 -[PART_OF]-> Fact1,
        Entity3 -[PART_OF {role: "subject"}]-> Fact2,
        Entity4 -[PART_OF {role: "object"}]-> Fact2,
        Entity5 -[PART_OF {role: "indirect_object"}]-> Fact2,
        Predicate2 -[PART_OF]-> Fact2,
        Record1 -[CONTAINS]-> Fact1,
        Record1 -[CONTAINS]-> Fact2,
        Record1 -[AUTHOR]-> Entity1,
    This schema allows you to represent the higher-level structure and context of the information,
    such as the fact that all the facts are part record.
    """

    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))
        self._insert_fact_query = '''
            CREATE (f:Fact {text: $fact_text, embedding: $embedding})
            WITH f
            UNWIND $entities as entity
            MATCH (e:Entity) WHERE id(e) = entity.id
            CREATE (e)-[:PART_OF {role: entity.role}]->(f)
            WITH f
            UNWIND $predicates as predicate_id
            MATCH (p:Predicate) WHERE id(p) = predicate_id
            CREATE (p)-[:PART_OF]->(f)
        '''

    def close(self):
        self._driver.close()

    def _execute_query(self, query, parameters=None, write=False):
        with self._driver.session() as session:
            if write:
                result = session.write_transaction(lambda tx: tx.run(query, parameters))
            else:
                result = session.read_transaction(lambda tx: tx.run(query, parameters))
            return list(result)

    def create_uniqueness_constraints(self):
        constraints = [
            {"name": "unique_entity_text", "label": "Entity", "property": "text"},
            {"name": "unique_predicate_text", "label": "Predicate", "property": "text"},
            {"name": "unique_fact_text", "label": "Fact", "property": "text"},
            {"name": "unique_record_text", "label": "Record", "property": "text"},
        ]

        for constraint in constraints:
            constraint_exists_query = f'''
                SHOW CONSTRAINTS WHERE name = '{constraint["name"]}'
            '''
            result = self._execute_query(constraint_exists_query)
            if len(result) == 0:
                create_constraint_query = f'''
                    CREATE CONSTRAINT {constraint["name"]} ON (n:{constraint["label"]})
                    ASSERT n.{constraint["property"]} IS UNIQUE
                '''
                self._execute_query(create_constraint_query, write=True)

    def find_or_create_entity(self, entity_text):
        query = '''
            MERGE (e:Entity {text: $entity_text})
            RETURN id(e) as entity_id
        '''
        parameters = {'entity_text': entity_text}
        result = self._execute_query(query, parameters)
        return result[0]['entity_id']

    def find_or_create_predicate(self, predicate_text: str) -> int:
        query = '''
            MERGE (p:Predicate {text: $predicate_text})
            RETURN id(p) as predicate_id
        '''
        parameters = {'predicate_text': predicate_text}
        result = self._execute_query(query, parameters)
        return result[0]['predicate_id']

    def find_or_create_fact(self, fact_text: str, embedding: list[float]) -> int:
        query = '''
            MERGE (f:Fact {text: $fact_text, embedding: $embedding})
            RETURN id(f) as fact_id
        '''
        parameters = {'fact_text': fact_text, 'embedding': embedding}
        result = self._execute_query(query, parameters)
        return result[0]['fact_id']

    def find_or_create_record(self, record_text: str) -> int:
        query = '''
            MERGE (r:Record {text: $record_text})
            RETURN id(r) as record_id
        '''
        parameters = {'record_text': record_text}
        result = self._execute_query(query, parameters)
        return result[0]['record_id']

    def insert_fact(self, fact_text: str, embedding: list[float], entities: list[str], predicates: list[str]):
        query = '''
            CREATE (f:Fact {text: $fact_text, embedding: $embedding})
            WITH f
            UNWIND $entities as entity_id
            MATCH (e:Entity) WHERE id(e) = entity_id
            CREATE (e)-[:PART_OF {role: entity.role}]->(f)
            WITH f
            UNWIND $predicates as predicate_id
            MATCH (p:Predicate) WHERE id(p) = predicate_id
            CREATE (p)-[:PART_OF]->(f)
            RETURN id(f) as fact_id
        '''
        entity_ids = [
            self.find_or_create_entity(entity) for entity in entities
        ]
        predicate_ids = [
            self.find_or_create_predicate(predicate) for predicate in predicates
        ]
        parameters = {
            'fact_text': fact_text,
            'embedding': embedding,
            'entities': entity_ids,
            'predicates': predicate_ids
        }
        result = self._execute_query(query, parameters, write=True)
        return result[0]['fact_id']

    def bind_facts_to_record(self, timestamp, fact_ids: int, author=None) -> int:
        query = '''
            CREATE (r:Record {timestamp: $timestamp})
            WITH r
            UNWIND $fact_ids as fact_id
            MATCH (f:Fact) WHERE id(f) = fact_id
            CREATE (r)-[:CONTAINS]->(r)
        '''
        parameters = {'timestamp': timestamp, 'fact_ids': fact_ids}

        if author:
            query += '''
                WITH r
                MATCH (e:Entity {text: author})
                CREATE (e)-[:AUTHOR]->(r)
            '''
            parameters['author'] = author

        query += '''
            RETURN id(r) as record_id
        '''
        result = self._execute_query(query, parameters, write=True)
        return result[0]['record_id']

