import pandas as pd
import numpy as np
from itertools import combinations
import json
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Apriori:
    def __init__(self, min_support=0.1, min_confidence=0.5):
        """
        初始化Apriori算法
        :param min_support: 最小支持度阈值
        :param min_confidence: 最小置信度阈值
        """
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.frequent_itemsets = []
        self.association_rules = []
    
    def fit(self, transactions):
        """
        执行Apriori算法，生成频繁项集和关联规则
        :param transactions: 事务列表，每个事务是一个项的集合
        :return: 频繁项集和关联规则
        """
        # 1. 生成候选项集C1
        C1 = self._create_C1(transactions)
        # 2. 生成频繁项集L1
        L1, support_data = self._scan_D(transactions, C1)
        self.frequent_itemsets = [L1]
        
        k = 2
        # 3. 迭代生成更高阶的频繁项集
        while len(self.frequent_itemsets[k-2]) > 0:
            # 生成候选项集Ck
            Ck = self._apriori_gen(self.frequent_itemsets[k-2], k)
            # 生成频繁项集Lk
            Lk, support_k = self._scan_D(transactions, Ck)
            support_data.update(support_k)
            
            if len(Lk) == 0:
                break
            self.frequent_itemsets.append(Lk)
            k += 1
        
        # 4. 生成关联规则
        self.association_rules = self._generate_rules(support_data)
        
        return self.frequent_itemsets, self.association_rules
    
    def _create_C1(self, transactions):
        """
        生成所有单个元素组成的候选项集
        :param transactions: 事务列表
        :return: 候选单元素项集
        """
        C1 = set()
        for transaction in transactions:
            for item in transaction:
                C1.add(frozenset([item]))
        return C1
    
    def _scan_D(self, transactions, Ck):
        """
        从候选项集中筛选出频繁项集
        :param transactions: 事务列表
        :param Ck: 候选项集
        :return: 频繁项集和支持度
        """
        D = list(map(set, transactions))
        ss_cnt = {}
        for tid in D:
            for can in Ck:
                if can.issubset(tid):
                    if can not in ss_cnt:
                        ss_cnt[can] = 1
                    else:
                        ss_cnt[can] += 1
        
        num_items = float(len(D))
        ret_list = []
        support_data = {}
        
        for key in ss_cnt:
            support = ss_cnt[key] / num_items
            if support >= self.min_support:
                ret_list.insert(0, key)
            support_data[key] = support
        
        return ret_list, support_data
    
    def _apriori_gen(self, Lk_1, k):
        """
        根据Lk-1生成Ck
        :param Lk_1: 频繁项集Lk-1
        :param k: 项集大小
        :return: 候选项集Ck
        """
        ret_list = []
        len_Lk_1 = len(Lk_1)
        
        for i in range(len_Lk_1):
            for j in range(i+1, len_Lk_1):
                L1 = list(Lk_1[i])[:k-2]
                L2 = list(Lk_1[j])[:k-2]
                L1.sort()
                L2.sort()
                
                if L1 == L2:
                    ret_list.append(Lk_1[i] | Lk_1[j])
        
        return ret_list
    
    def _generate_rules(self, support_data):
        """
        生成关联规则
        :param support_data: 支持度数据
        :return: 关联规则列表
        """
        big_rules_list = []
        # 从2阶频繁项集开始
        for i in range(1, len(self.frequent_itemsets)):
            for freq_set in self.frequent_itemsets[i]:
                # 生成所有非空子集
                H1 = [frozenset([item]) for item in freq_set]
                if i > 1:
                    # 处理3阶及以上的频繁项集
                    self._rules_from_conseq(freq_set, H1, support_data, big_rules_list)
                else:
                    # 处理2阶频繁项集
                    self._calc_conf(freq_set, H1, support_data, big_rules_list)
        return big_rules_list
    
    def _calc_conf(self, freq_set, H, support_data, brl):
        """
        计算置信度并生成规则
        :param freq_set: 频繁项集
        :param H: 后件候选集
        :param support_data: 支持度数据
        :param brl: 关联规则列表
        :return: 满足最小置信度的后件
        """
        pruned_H = []
        for conseq in H:
            # 前件 = 频繁项集 - 后件
            antecedent = freq_set - conseq
            # 置信度 = 支持度(freq_set) / 支持度(antecedent)
            conf = support_data[freq_set] / support_data[antecedent]
            if conf >= self.min_confidence:
                # 添加规则到结果列表
                brl.append({
                    'antecedent': list(antecedent),
                    'consequent': list(conseq),
                    'support': support_data[freq_set],
                    'confidence': conf,
                    'lift': conf / support_data[conseq] if support_data[conseq] > 0 else 0
                })
                pruned_H.append(conseq)
        return pruned_H
    
    def _rules_from_conseq(self, freq_set, H, support_data, brl):
        """
        从后件生成更多规则
        :param freq_set: 频繁项集
        :param H: 后件候选集
        :param support_data: 支持度数据
        :param brl: 关联规则列表
        """
        m = len(H[0])
        if len(freq_set) > (m + 1):
            # 生成m+1阶的后件
            Hmp1 = self._apriori_gen(H, m + 1)
            # 计算置信度
            Hmp1 = self._calc_conf(freq_set, Hmp1, support_data, brl)
            if len(Hmp1) > 1:
                # 递归生成更多规则
                self._rules_from_conseq(freq_set, Hmp1, support_data, brl)
    
    def save_results(self, output_dir, filename='apriori_results.json'):
        """
        保存关联规则结果到JSON文件
        :param output_dir: 输出目录
        :param filename: 输出文件名
        """
        rules_dict = {
            'rules': self.association_rules,
            'frequent_itemsets': [
                [list(itemset) for itemset in Lk]
                for Lk in self.frequent_itemsets
            ]
        }
        
        output_path = Path(output_dir) / filename
        # 确保使用UTF-8编码保存，并且不转义中文
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(rules_dict, f, ensure_ascii=False, indent=2)


def main():
    # 示例用法
    transactions = [
        ['A', 'B', 'C'],
        ['A', 'B'],
        ['A', 'B', 'D'],
        ['B', 'E'],
        ['B', 'C', 'E'],
        ['A', 'C'],
        ['A', 'B', 'C', 'E'],
        ['A', 'B', 'C', 'D', 'E']
    ]
    
    apriori = Apriori(min_support=0.3, min_confidence=0.7)
    frequent_itemsets, rules = apriori.fit(transactions)
    
    print("频繁项集:")
    for i, Lk in enumerate(frequent_itemsets):
        print(f"L{i+1}: {[[item for item in itemset] for itemset in Lk]}")
    
    print("\n关联规则:")
    for rule in rules:
        print(f"{rule['antecedent']} => {rule['consequent']} (支持度: {rule['support']:.3f}, 置信度: {rule['confidence']:.3f}, lift: {rule['lift']:.3f})")


if __name__ == '__main__':
    main()
