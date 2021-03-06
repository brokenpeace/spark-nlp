import unittest

from pyspark.ml import Pipeline
from sparknlp.annotator import *
from sparknlp.base import *
from test.util import SparkContextForTest, SparkContextForNER


class BasicAnnotatorsTestSpec(unittest.TestCase):

    def setUp(self):
        # This implicitly sets up py4j for us
        self.data = SparkContextForTest.data

    def runTest(self):
        document_assembler = DocumentAssembler() \
            .setInputCol("text") \
            .setOutputCol("document")
        tokenizer = RegexTokenizer()\
            .setOutputCol("token")
        stemmer = Stemmer() \
            .setInputCols(["token"]) \
            .setOutputCol("stem")
        normalizer = Normalizer() \
            .setInputCols(["stem"]) \
            .setOutputCol("normalize")
        token_assembler = TokenAssembler() \
            .setInputCols(["normalize"]) \
            .setOutputCol("assembled")
        finisher = Finisher() \
            .setInputCols(["assembled"]) \
            .setOutputCols(["reassembled_view"])
        assembled = document_assembler.transform(self.data)
        tokenized = tokenizer.transform(assembled)
        stemmed = stemmer.transform(tokenized)
        normalized = normalizer.transform(stemmed)
        reassembled = token_assembler.transform(normalized)
        finisher.transform(reassembled).show()


class RegexMatcherTestSpec(unittest.TestCase):

    def setUp(self):
        # This implicitly sets up py4j for us
        self.data = SparkContextForTest.data

    def runTest(self):
        document_assembler = DocumentAssembler() \
            .setInputCol("text") \
            .setOutputCol("document")
        regex_matcher = RegexMatcher() \
            .setStrategy("MATCH_ALL") \
            .setRulesPath("../src/test/resources/regex-matcher/rules.txt") \
            .setOutputCol("regex")
        assembled = document_assembler.transform(self.data)
        regex_matcher.transform(assembled).show()


class LemmatizerTestSpec(unittest.TestCase):

    def setUp(self):
        self.data = SparkContextForTest.data

    def runTest(self):
        document_assembler = DocumentAssembler() \
            .setInputCol("text") \
            .setOutputCol("document")
        tokenizer = RegexTokenizer() \
            .setOutputCol("token")
        lemmatizer = Lemmatizer() \
            .setInputCols(["token"]) \
            .setOutputCol("lemma") \
            .setDictionary("../src/test/resources/lemma-corpus/AntBNC_lemmas_ver_001.txt")
        assembled = document_assembler.transform(self.data)
        tokenized = tokenizer.transform(assembled)
        lemmatizer.transform(tokenized).show()


class DateMatcherTestSpec(unittest.TestCase):

    def setUp(self):
        self.data = SparkContextForTest.data

    def runTest(self):
        document_assembler = DocumentAssembler() \
            .setInputCol("text") \
            .setOutputCol("document")
        date_matcher = DateMatcher() \
            .setOutputCol("date") \
            .setDateFormat("yyyyMM")
        assembled = document_assembler.transform(self.data)
        date_matcher.transform(assembled).show()


class EntityExtractorTestSpec(unittest.TestCase):

    def setUp(self):
        self.data = SparkContextForTest.data

    def runTest(self):
        document_assembler = DocumentAssembler() \
            .setInputCol("text") \
            .setOutputCol("document")
        entity_extractor = EntityExtractor() \
            .setMaxLen(4) \
            .setOutputCol("entity")
        assembled = document_assembler.transform(self.data)
        entity_extractor.transform(assembled).show()


class PerceptronApproachTestSpec(unittest.TestCase):

    def setUp(self):
        self.data = SparkContextForTest.data

    def runTest(self):
        document_assembler = DocumentAssembler() \
            .setInputCol("text") \
            .setOutputCol("document")
        sentence_detector = SentenceDetectorModel() \
            .setInputCols(["document"]) \
            .setOutputCol("sentence")
        tokenizer = RegexTokenizer() \
            .setInputCols(["sentence"]) \
            .setOutputCol("token")
        pos_tagger = PerceptronApproach() \
            .setInputCols(["token", "sentence"]) \
            .setOutputCol("pos") \
            .setCorpusPath("../src/main/resources/anc-pos-corpus") \
            .setIterations(2) \
            .fit(self.data)
        assembled = document_assembler.transform(self.data)
        sentenced = sentence_detector.transform(assembled)
        tokenized = tokenizer.transform(sentenced)
        pos_tagger.transform(tokenized).show()


class RegexNERApproachTestSpec(unittest.TestCase):

    def setUp(self):
        self.data = SparkContextForNER.data

    def runTest(self):
        document_assembler = DocumentAssembler() \
            .setInputCol("_c0") \
            .setOutputCol("document")
        sentence_detector = SentenceDetectorModel() \
            .setInputCols(["document"]) \
            .setOutputCol("sentence")
        tokenizer = RegexTokenizer() \
            .setInputCols(["sentence"]) \
            .setOutputCol("token")
        ner_tagger = NERRegexApproach() \
            .setInputCols(["sentence"]) \
            .setOutputCol("NER") \
            .fit(self.data)
        assembled = document_assembler.transform(self.data)
        sentenced = sentence_detector.transform(assembled)
        tokenized = tokenizer.transform(sentenced)
        result = ner_tagger.transform(tokenized)
        result.select("NER").take(10)


class PragmaticSBDTestSpec(unittest.TestCase):

    def setUp(self):
        self.data = SparkContextForTest.data

    def runTest(self):
        document_assembler = DocumentAssembler() \
            .setInputCol("text") \
            .setOutputCol("document")
        sentence_detector = SentenceDetectorModel() \
            .setInputCols(["document"]) \
            .setOutputCol("sentence") \
            .setCustomBounds(["%%"])
        assembled = document_assembler.transform(self.data)
        sentence_detector.transform(assembled).show()


class PragmaticScorerTestSpec(unittest.TestCase):

    def setUp(self):
        self.data = SparkContextForTest.data

    def runTest(self):
        document_assembler = DocumentAssembler() \
            .setInputCol("text") \
            .setOutputCol("document")
        sentence_detector = SentenceDetectorModel() \
            .setInputCols(["document"]) \
            .setOutputCol("sentence")
        tokenizer = RegexTokenizer() \
            .setInputCols(["sentence"]) \
            .setOutputCol("token")
        lemmatizer = Lemmatizer() \
            .setInputCols(["token"]) \
            .setOutputCol("lemma") \
            .setDictionary({"missed": "miss"})
        sentiment_detector = SentimentDetectorModel() \
            .setInputCols(["lemma", "sentence"]) \
            .setOutputCol("sentiment")
        assembled = document_assembler.transform(self.data)
        sentenced = sentence_detector.transform(assembled)
        tokenized = tokenizer.transform(sentenced)
        lemmatized = lemmatizer.transform(tokenized)
        sentiment_detector.transform(lemmatized).show()


class PipelineTestSpec(unittest.TestCase):

    def setUp(self):
        self.data = SparkContextForTest.data

    def runTest(self):
        document_assembler = DocumentAssembler() \
            .setInputCol("text") \
            .setOutputCol("document")
        tokenizer = RegexTokenizer() \
            .setOutputCol("token")
        lemmatizer = Lemmatizer() \
            .setInputCols(["token"]) \
            .setOutputCol("lemma") \
            .setDictionary({"sad": "unsad"})
        finisher = Finisher() \
            .setInputCols(["token", "lemma"]) \
            .setOutputCols(["token_views", "lemma_views"])
        pipeline = Pipeline(stages=[document_assembler, tokenizer, lemmatizer, finisher])
        model = pipeline.fit(self.data)
        token_before_save = model.transform(self.data).select("token_views").take(1)[0].token_views.split("@")[2]
        lemma_before_save = model.transform(self.data).select("lemma_views").take(1)[0].lemma_views.split("@")[2]
        pipe_path = "./tmp_pipeline"
        pipeline.write().overwrite().save(pipe_path)
        loaded_pipeline = Pipeline.read().load(pipe_path)
        token_after_save = model.transform(self.data).select("token_views").take(1)[0].token_views.split("@")[2]
        lemma_after_save = model.transform(self.data).select("lemma_views").take(1)[0].lemma_views.split("@")[2]
        print(token_before_save)
        assert token_before_save == "sad"
        assert lemma_before_save == "unsad"
        assert token_after_save == token_before_save
        assert lemma_after_save == lemma_before_save
        loaded_pipeline.fit(self.data).transform(self.data).show()


class SpellCheckerTestSpec(unittest.TestCase):

    def setUp(self):
        self.data = SparkContextForTest.data

    def runTest(self):
        document_assembler = DocumentAssembler() \
            .setInputCol("text") \
            .setOutputCol("document")
        tokenizer = RegexTokenizer() \
            .setOutputCol("token")
        spell_checker = NorvigSweetingApproach() \
            .setInputCols(["token"]) \
            .setOutputCol("spell") \
            .setCorpusPath("../src/test/resources/spell/sherlockholmes.txt") \
            .fit(self.data)
        assembled = document_assembler.transform(self.data)
        tokenized = tokenizer.transform(assembled)
        checked = spell_checker.transform(tokenized)
        checked.show()
