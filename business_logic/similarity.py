import jellyfish

class Similarity:

    def get_similarity(self, stored_req, incoming_req):
        # Check for exact match of keys
        keys_match = set(stored_req.keys()) == set(incoming_req.keys())
        common_parameters_score = len(set(stored_req.keys()).intersection(set(incoming_req.keys()))) / len(set(stored_req.keys()))
        keys_similarity_weight = 0.7 if keys_match else common_parameters_score  # Adjust weights as needed
        #print(common_parameters_score)
        # Calculate content similarity for common keys
        content_similarity_scores = []
        for key in set(stored_req.keys()).intersection(set(incoming_req.keys())):
            value1 = stored_req[key]
            value2 = incoming_req[key]

            # Calculate similarity based on data type
            if isinstance(value1, (int)) and isinstance(value2, (int)):
                similarity = self.numeric_similarity(value1, value2)
            elif isinstance(value1, (float)) and isinstance(value2, (float)):
                similarity = self.numeric_similarity(value1, value2)

            else:
                similarity = self.string_similarity(value1, value2)

            #print(f"similarity of values {value1, value2}, {similarity}")
            content_similarity_scores.append(similarity)

        if content_similarity_scores:
            content_similarity = sum(content_similarity_scores) / len(content_similarity_scores)
        else:
            content_similarity = 0.0  # No common keys

        # Combine the overall similarity score, giving more weight to key similarity
        overall_similarity = (keys_similarity_weight + content_similarity) / (keys_similarity_weight + 1)
        return overall_similarity

    def numeric_similarity(self,value1, value2):
        max_value = max(value1, value2)
        min_value = min(value1, value2)

        abs_difference = max_value - min_value
        threshold = 50  # Adjust if necessary

        # Calculate similarity based on the absolute difference
        if abs_difference <= threshold:
            similarity = 1.0 - (abs_difference / threshold)
        else:
            similarity = 0
        return similarity

    def string_similarity(self,value1, value2):
        return jellyfish.jaro_winkler_similarity(value1, value2)

