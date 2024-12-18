import re

class_label = ""
total_class_token = {}

# print(vocabulary)
class_eachtoken_count = {} 

for class_label in class_labels: 
   total_class_token[class_label] = 0
   class_eachtoken_count[class_label] = {}
   for voc in vocabulary:
      class_eachtoken_count[class_label] [voc] = 0

   doccount = 0
   total_voca_count = 0
   for doc in doc_list:
      words = word_tokenize(doc);

      class_label = temp_class_labels[doccount]

      for word in words:
         if word in vocabulary:
            class_eachtoken_count[class_label][word] = class_eachtoken_count[class_label][word] + 1 
            total_class_token[class_label] = total_class_token[class_label] + 1
            #print("total_class_token is ",total_class_token)
            total_voca_count = total_voca_count + 1

      doccount = doccount + 1

   doc = re.sub("\d+"," ",doc)
   result_doc = word_tokenize(doc)
   tagged_sentence = nltk.pos_tag(result_doc)
   edited_sentence = [word for word,tag in tagged_sentence if tag != 'NNP' and tag != 'NNPS' and tag != 'NNS' and tag != 'NN' and tag != 'JJ' and tag != 'JJR' and tag != 'JJS']