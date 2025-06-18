import os
import re
import docx
import pandas as pd
import argparse
from datetime import datetime

def extract_qa_blocks(text):
    """
    通用问答抽取逻辑：支持 问题/问 + 回答/答 结构
    """
    qa_pairs = []
    pattern = re.compile(r'(?:问题|问)[：:]\s*(.*?)(?:回答|答)[：:]\s*(.*?)(?=(?:问题|问)[：:]|$)', re.DOTALL)
    matches = pattern.findall(text)

    for q, a in matches:
        q = q.strip().replace('\n', ' ')
        a = a.strip().replace('\n', ' ')
        qa_pairs.append({'question': q, 'answer': a})

    return qa_pairs

def read_docx_extract_qa(file_path):
    """
    读取单个 docx 文件并尝试提取问答
    """
    try:
        doc = docx.Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        qa_pairs = extract_qa_blocks(text)

        # 兜底策略：按段落简单匹配
        if not qa_pairs:
            paras = text.split('\n')
            question, answer = '', ''
            for line in paras:
                if line.startswith(('问', '问题')):
                    question = re.sub(r'^(问题|问)[：:]', '', line).strip()
                elif line.startswith(('答', '回答')):
                    answer = re.sub(r'^(回答|答)[：:]', '', line).strip()
                    qa_pairs.append({'question': question, 'answer': answer})
        return qa_pairs
    except Exception as e:
        print(f"❌ 读取文件失败: {file_path} 错误信息: {e}")
        return []

def batch_process(input_folder, output_file='cleaned_output.csv'):
    """
    批量处理整个文件夹下所有 docx 文件
    """
    data = []
    total_files = 0
    for file in os.listdir(input_folder):
        if file.endswith('.docx'):
            file_path = os.path.join(input_folder, file)
            qa_pairs = read_docx_extract_qa(file_path)
            for pair in qa_pairs:
                pair['source_file'] = file
                data.append(pair)
            total_files += 1
            print(f"✅ 已处理文件: {file} （累计 {total_files} 个文件）")

    if data:
        df = pd.DataFrame(data)
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n🎯 清洗完成，共处理 {total_files} 个文件，共提取 {len(df)} 条问答，保存至 {output_file}")
    else:
        print("⚠ 未提取到任何问答数据，请检查源文件格式。")

def main():
    parser = argparse.ArgumentParser(description="通用 Docx 问答清洗工具")
    parser.add_argument('--input_folder', type=str, required=True, help="包含 docx 文件的文件夹路径")
    parser.add_argument('--output_file', type=str, default=None, help="输出 CSV 文件名")
    args = parser.parse_args()

    if not args.output_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        args.output_file = f"cleaned_output_{timestamp}.csv"

    if not os.path.exists(args.input_folder):
        print(f"❌ 输入文件夹不存在: {args.input_folder}")
        return

    batch_process(args.input_folder, args.output_file)

if __name__ == '__main__':
    main()
