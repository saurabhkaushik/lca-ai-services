
class Highlight_Service:
    def __init__(self) -> None:
        pass

    def get_flag(self, score):
        #score = int (((score - present_base_score) / (100 - present_base_score)) * 100)
        flag = ''
        if score < 40:
            flag = "LOW"
        else:
            if score >= 40 and score <= 80:
                flag = "MEDIUM"
            else:
                if score > 80:
                    flag = "HIGH"
        return flag

    def highlight_text(self, trans_resp, threshold):
        highlight_results = []

        for key in trans_resp:
            highlight_dict = {}
            highlight_dict['c_sentence'] = trans_resp[key]['sentence']
            highlight_dict['label'] = trans_resp[key]['label'].capitalize()  

            highlight_dict['p_score'] = int(trans_resp[key]['presence_score'])
            highlight_dict['c_score'] = int(trans_resp[key]['context_score'])
            highlight_dict['risk_score'] = int(trans_resp[key]['risk_score'])               
                      
            if highlight_dict['p_score'] >= threshold:                
                flag = self.get_flag(highlight_dict['c_score']) 
                highlight_dict['flag'] = flag.capitalize()
            else: 
                highlight_dict['flag'] = 'NA'
            highlight_results.append(highlight_dict)

        return highlight_results


    def analyse_results(self, trans_resp, threshold):
        score_presence_count_total = 0
        score_context_high_count = 0
        score_context_medium_count = 0
        score_context_low_count = 0
        score_risk_sents = 0
        class_analysis = {}
        score_presence_count_json = {}
        for key in trans_resp:
            label = trans_resp[key]['label']  

            p_score = int(trans_resp[key]['presence_score'])
            c_score = int(trans_resp[key]['context_score'])
            risk_score = int(trans_resp[key]['risk_score'])               
                      
            if p_score >= threshold:
                score_risk_sents += risk_score
                score_presence_count_total += 1
                if label in score_presence_count_json.keys(): 
                    score_presence_count_json[label] += 1
                else: 
                    score_presence_count_json[label] = 1

                if not label in class_analysis.keys():
                    class_analysis[label]= {'count': 0, 'score': 0}
                else: 
                    class_analysis[label]['count'] += 1 
                    class_analysis[label]['score'] += c_score
                
                flag = self.get_flag(c_score) 
                if flag == "HIGH":
                    score_context_high_count += 1
                elif flag == "MEDIUM":
                    score_context_medium_count += 1
                elif flag == "LOW":
                    score_context_low_count += 1

        # Context Scoring 
        score_report_risk_score = 0
        if score_presence_count_total != 0:
            score_report_risk_score = (score_risk_sents / score_presence_count_total)

        # Context Strength Percentage based on Score 
        score_report_json = {'score_report_risk_score': int(score_report_risk_score)}
        # Context Count Percentage based on Counts  
        score_context_count_json = {'score_context_high_count' : int(score_context_high_count), 'score_context_medium_count' : int(score_context_medium_count), 'score_context_low_count' : int(score_context_low_count)}
        
        label_keys = list(score_presence_count_json.keys())
        label_values = list(score_presence_count_json.values())
        score_presence_data = score_presence_count_json
        #score_presence_count_json['label_keys'] = label_keys
        #score_presence_count_json['label_values'] = label_values

        class_analysis_data = {} 
        for data in class_analysis: 
            if class_analysis[data]['count'] == 0:
                class_analysis[data]['avg'] = 0
            else: 
                class_analysis[data]['avg'] = class_analysis[data]['score'] / class_analysis[data]['count']
            class_analysis_data[data] = class_analysis[data]['avg']

        report_analysis = {}
        report_analysis['score_report_json'] = score_report_json
        report_analysis['score_context_count_json'] = score_context_count_json
        report_analysis['score_presence_count_json'] = score_presence_count_json
        report_analysis['score_presence_data'] = score_presence_data
        report_analysis['class_analysis_data'] = class_analysis_data
        print('Label Class Strength:', report_analysis['class_analysis_data'])
        print ('score_report_json:', report_analysis['score_report_json'])
        print ('score_context_count_json:', report_analysis['score_context_count_json'])
        print ('score_presence_count_json:', report_analysis['score_presence_count_json'])
        return report_analysis
