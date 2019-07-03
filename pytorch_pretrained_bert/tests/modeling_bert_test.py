# coding=utf-8
# Copyright 2018 The Google AI Language Team Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest
import shutil
import pytest

from pytorch_pretrained_bert import (BertConfig, BertModel, BertForMaskedLM,
                                     BertForNextSentencePrediction, BertForPreTraining,
                                     BertForQuestionAnswering, BertForSequenceClassification,
                                     BertForTokenClassification, BertForMultipleChoice)
from pytorch_pretrained_bert.modeling_bert import PRETRAINED_MODEL_ARCHIVE_MAP

from .model_tests_commons import (create_and_check_commons, ConfigTester, ids_tensor)


class BertModelTest(unittest.TestCase):
    class BertModelTester(object):

        def __init__(self,
                     parent,
                     batch_size=13,
                     seq_length=7,
                     is_training=True,
                     use_input_mask=True,
                     use_token_type_ids=True,
                     use_labels=True,
                     vocab_size=99,
                     hidden_size=32,
                     num_hidden_layers=5,
                     num_attention_heads=4,
                     intermediate_size=37,
                     hidden_act="gelu",
                     hidden_dropout_prob=0.1,
                     attention_probs_dropout_prob=0.1,
                     max_position_embeddings=512,
                     type_vocab_size=16,
                     type_sequence_label_size=2,
                     initializer_range=0.02,
                     num_labels=3,
                     num_choices=4,
                     scope=None,
                     all_model_classes = (BertModel, BertForMaskedLM, BertForNextSentencePrediction,
                             BertForPreTraining, BertForQuestionAnswering, BertForSequenceClassification,
                             BertForTokenClassification),
                    ):
            self.parent = parent
            self.batch_size = batch_size
            self.seq_length = seq_length
            self.is_training = is_training
            self.use_input_mask = use_input_mask
            self.use_token_type_ids = use_token_type_ids
            self.use_labels = use_labels
            self.vocab_size = vocab_size
            self.hidden_size = hidden_size
            self.num_hidden_layers = num_hidden_layers
            self.num_attention_heads = num_attention_heads
            self.intermediate_size = intermediate_size
            self.hidden_act = hidden_act
            self.hidden_dropout_prob = hidden_dropout_prob
            self.attention_probs_dropout_prob = attention_probs_dropout_prob
            self.max_position_embeddings = max_position_embeddings
            self.type_vocab_size = type_vocab_size
            self.type_sequence_label_size = type_sequence_label_size
            self.initializer_range = initializer_range
            self.num_labels = num_labels
            self.num_choices = num_choices
            self.scope = scope
            self.all_model_classes = all_model_classes

        def prepare_config_and_inputs(self):
            input_ids = ids_tensor([self.batch_size, self.seq_length], self.vocab_size)

            input_mask = None
            if self.use_input_mask:
                input_mask = ids_tensor([self.batch_size, self.seq_length], vocab_size=2)

            token_type_ids = None
            if self.use_token_type_ids:
                token_type_ids = ids_tensor([self.batch_size, self.seq_length], self.type_vocab_size)

            sequence_labels = None
            token_labels = None
            choice_labels = None
            if self.use_labels:
                sequence_labels = ids_tensor([self.batch_size], self.type_sequence_label_size)
                token_labels = ids_tensor([self.batch_size, self.seq_length], self.num_labels)
                choice_labels = ids_tensor([self.batch_size], self.num_choices)

            config = BertConfig(
                vocab_size_or_config_json_file=self.vocab_size,
                hidden_size=self.hidden_size,
                num_hidden_layers=self.num_hidden_layers,
                num_attention_heads=self.num_attention_heads,
                intermediate_size=self.intermediate_size,
                hidden_act=self.hidden_act,
                hidden_dropout_prob=self.hidden_dropout_prob,
                attention_probs_dropout_prob=self.attention_probs_dropout_prob,
                max_position_embeddings=self.max_position_embeddings,
                type_vocab_size=self.type_vocab_size,
                initializer_range=self.initializer_range)

            return config, input_ids, token_type_ids, input_mask, sequence_labels, token_labels, choice_labels

        def check_loss_output(self, result):
            self.parent.assertListEqual(
                list(result["loss"].size()),
                [])

        def create_and_check_bert_model(self, config, input_ids, token_type_ids, input_mask, sequence_labels, token_labels, choice_labels):
            model = BertModel(config=config)
            model.eval()
            sequence_output, pooled_output = model(input_ids, token_type_ids, input_mask)

            result = {
                "sequence_output": sequence_output,
                "pooled_output": pooled_output,
            }
            self.parent.assertListEqual(
                list(result["sequence_output"].size()),
                [self.batch_size, self.seq_length, self.hidden_size])
            self.parent.assertListEqual(list(result["pooled_output"].size()), [self.batch_size, self.hidden_size])


        def create_and_check_bert_for_masked_lm(self, config, input_ids, token_type_ids, input_mask, sequence_labels, token_labels, choice_labels):
            model = BertForMaskedLM(config=config)
            model.eval()
            loss, prediction_scores = model(input_ids, token_type_ids, input_mask, token_labels)
            result = {
                "loss": loss,
                "prediction_scores": prediction_scores,
            }
            self.parent.assertListEqual(
                list(result["prediction_scores"].size()),
                [self.batch_size, self.seq_length, self.vocab_size])
            self.check_loss_output(result)

        def create_and_check_bert_for_next_sequence_prediction(self, config, input_ids, token_type_ids, input_mask, sequence_labels, token_labels, choice_labels):
            model = BertForNextSentencePrediction(config=config)
            model.eval()
            loss, seq_relationship_score = model(input_ids, token_type_ids, input_mask, sequence_labels)
            result = {
                "loss": loss,
                "seq_relationship_score": seq_relationship_score,
            }
            self.parent.assertListEqual(
                list(result["seq_relationship_score"].size()),
                [self.batch_size, 2])
            self.check_loss_output(result)


        def create_and_check_bert_for_pretraining(self, config, input_ids, token_type_ids, input_mask, sequence_labels, token_labels, choice_labels):
            model = BertForPreTraining(config=config)
            model.eval()
            loss, prediction_scores, seq_relationship_score = model(input_ids, token_type_ids, input_mask, token_labels, sequence_labels)
            result = {
                "loss": loss,
                "prediction_scores": prediction_scores,
                "seq_relationship_score": seq_relationship_score,
            }
            self.parent.assertListEqual(
                list(result["prediction_scores"].size()),
                [self.batch_size, self.seq_length, self.vocab_size])
            self.parent.assertListEqual(
                list(result["seq_relationship_score"].size()),
                [self.batch_size, 2])
            self.check_loss_output(result)


        def create_and_check_bert_for_question_answering(self, config, input_ids, token_type_ids, input_mask, sequence_labels, token_labels, choice_labels):
            model = BertForQuestionAnswering(config=config)
            model.eval()
            loss, start_logits, end_logits = model(input_ids, token_type_ids, input_mask, sequence_labels, sequence_labels)
            result = {
                "loss": loss,
                "start_logits": start_logits,
                "end_logits": end_logits,
            }
            self.parent.assertListEqual(
                list(result["start_logits"].size()),
                [self.batch_size, self.seq_length])
            self.parent.assertListEqual(
                list(result["end_logits"].size()),
                [self.batch_size, self.seq_length])
            self.check_loss_output(result)


        def create_and_check_bert_for_sequence_classification(self, config, input_ids, token_type_ids, input_mask, sequence_labels, token_labels, choice_labels):
            config.num_labels = self.num_labels
            model = BertForSequenceClassification(config)
            model.eval()
            loss, logits = model(input_ids, token_type_ids, input_mask, sequence_labels)
            result = {
                "loss": loss,
                "logits": logits,
            }
            self.parent.assertListEqual(
                list(result["logits"].size()),
                [self.batch_size, self.num_labels])
            self.check_loss_output(result)


        def create_and_check_bert_for_token_classification(self, config, input_ids, token_type_ids, input_mask, sequence_labels, token_labels, choice_labels):
            config.num_labels = self.num_labels
            model = BertForTokenClassification(config=config)
            model.eval()
            loss, logits = model(input_ids, token_type_ids, input_mask, token_labels)
            result = {
                "loss": loss,
                "logits": logits,
            }
            self.parent.assertListEqual(
                list(result["logits"].size()),
                [self.batch_size, self.seq_length, self.num_labels])
            self.check_loss_output(result)


        def create_and_check_bert_for_multiple_choice(self, config, input_ids, token_type_ids, input_mask, sequence_labels, token_labels, choice_labels):
            config.num_choices = self.num_choices
            model = BertForMultipleChoice(config=config)
            model.eval()
            multiple_choice_inputs_ids = input_ids.unsqueeze(1).expand(-1, self.num_choices, -1).contiguous()
            multiple_choice_token_type_ids = token_type_ids.unsqueeze(1).expand(-1, self.num_choices, -1).contiguous()
            multiple_choice_input_mask = input_mask.unsqueeze(1).expand(-1, self.num_choices, -1).contiguous()
            loss, logits = model(multiple_choice_inputs_ids,
                         multiple_choice_token_type_ids,
                         multiple_choice_input_mask,
                         choice_labels)
            result = {
                "loss": loss,
                "logits": logits,
            }
            self.parent.assertListEqual(
                list(result["logits"].size()),
                [self.batch_size, self.num_choices])
            self.check_loss_output(result)


        def create_and_check_bert_commons(self, config, input_ids, token_type_ids, input_mask, sequence_labels, token_labels, choice_labels):
            inputs_dict = {'input_ids': input_ids, 'token_type_ids': token_type_ids, 'attention_mask': input_mask}
            create_and_check_commons(self, config, inputs_dict)

    def test_default(self):
        self.run_tester(BertModelTest.BertModelTester(self))

    def test_config(self):
        config_tester = ConfigTester(self, config_class=BertConfig, hidden_size=37)
        config_tester.run_common_tests()

    @pytest.mark.slow
    def test_model_from_pretrained(self):
        cache_dir = "/tmp/pytorch_pretrained_bert_test/"
        for model_name in list(PRETRAINED_MODEL_ARCHIVE_MAP.keys())[:1]:
            model = BertModel.from_pretrained(model_name, cache_dir=cache_dir)
            shutil.rmtree(cache_dir)
            self.assertIsNotNone(model)

    def run_tester(self, tester):
        config_and_inputs = tester.prepare_config_and_inputs()
        tester.create_and_check_bert_model(*config_and_inputs)

        config_and_inputs = tester.prepare_config_and_inputs()
        tester.create_and_check_bert_for_masked_lm(*config_and_inputs)

        config_and_inputs = tester.prepare_config_and_inputs()
        tester.create_and_check_bert_for_multiple_choice(*config_and_inputs)

        config_and_inputs = tester.prepare_config_and_inputs()
        tester.create_and_check_bert_for_next_sequence_prediction(*config_and_inputs)

        config_and_inputs = tester.prepare_config_and_inputs()
        tester.create_and_check_bert_for_pretraining(*config_and_inputs)

        config_and_inputs = tester.prepare_config_and_inputs()
        tester.create_and_check_bert_for_question_answering(*config_and_inputs)

        config_and_inputs = tester.prepare_config_and_inputs()
        tester.create_and_check_bert_for_sequence_classification(*config_and_inputs)

        config_and_inputs = tester.prepare_config_and_inputs()
        tester.create_and_check_bert_for_token_classification(*config_and_inputs)

        config_and_inputs = tester.prepare_config_and_inputs()
        tester.create_and_check_bert_commons(*config_and_inputs)

if __name__ == "__main__":
    unittest.main()