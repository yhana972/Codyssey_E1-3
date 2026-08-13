import json

def load_json_data(file_path: str):
    '''
        Json 데이터 로드 함수
        input : file_path 
        output : data
        Flow : JSON 파일 열기 -> 데이터 읽기 -> dict 반환
    '''
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data

def calculate_mac(pattern: list, filter_data: list) -> float:
    '''
        MAC 연산 함수(패턴과 필터의 사이즈가 동일하다라는 가정하에)
        input : pattern, filter_data
        output : score
        Flow : MAC연산 ->  score 반환
    '''
    score = 0.0 
    size = len(pattern)

    for row in range(size):
        for col in range(size):
            score += pattern[row][col] * filter_data[row][col]

    return score
        
def validate_matrix(array : list) -> bool:
    '''
        데이터 검증 함수 | 배열 자체가 N×N으로 정상인가?
        input : array
        output : False or True
        Flow : array의 행 갯수 계산 -> array의 행 갯수만큼 for문 -> 
        각 열의 갯수와 array의 행 갯수가 같은지 비교 -> result
    '''
    size = len(array)

    #array 행 갯수가 0이면 빈 배열이므로 계산 불가.
    if size == 0 :  
        return False

    for row in array:
        # 현재 행의 열 개수가 전체 행 개수와 다르면 N×N 배열이 아니므로 계산 불가
        if len(row) != size:
            return False

    return True

def validate_same_size(pattern: list, filter_data: list) -> bool:
    '''
        데이터 검증 함수 | 두 배열의 N이 같은가?
        input : pattern, filter_data
        output : False or True
        Flow : patter과 filter_data 사이즈 비교 -> result
    '''
    return len(pattern) == len(filter_data)

def input_matrix(name: str, size: int = 3)-> list:
    '''
        모드 1 : 사용자 입력 (3 X 3)
        input : name, size
        output : matrix
        Flow :  사용자 입력 -> 공백 기준으로 나눔 -> 각 문자열 실수 변환 -> 완성된 한 행을 전체 배열에 넣고 -> 그 행들을 모아 2차원 배열로 return 
    '''
    matrix = []

    print()
    print(f"{name} 입력 (3줄 입력, 공백 구분) :")
    while len(matrix) < size: # matrix에 저장된 정상 행 개수가 size보다 작은 동안 계속 반복.
        line = input()
        values = line.split()
        if len(values) != size:
            print(
                    f"입력 형식 오류: 각 줄에 {size}개의 숫자를 "
                    "공백으로 구분해 입력하세요."
                )
            continue
        try:
            numbers = []
                
            for value in values:
                numbers.append(float(value))
            matrix.append(numbers)

        except ValueError:
            print("숫자를 입력해주세요.")
            continue
    return matrix

def normalize_label():
    pass

def decide_pattern(score_a: float, score_b:float) -> str:
    '''
        점수 비교 판정 함수
        input : score_a, score_b
        output : 판정 결과
        Flow : score_a, score_b 점수 비교 -> 판정
    '''
    # 두 점수의 차이가 1e-9보다 작으면 부동소수점 연산에서 발생할 수 있는 미세한 오차로 보고 동점으로 처리한다.
    if abs(score_a - score_b) < 1e-9:
        return "UNDECIDED"

    if score_a > score_b:
        return "A"
    else:
        return "B"

def run_user_mode():
    '''
        사용자 모드 실행 함수
        Flow : 필터 A 입력 -> 필터 B 입력 -> 패턴 입력 -> MAC(A) 계산 -> MAC(B) 계산 -> 점수 출력
    '''
    filter_a = input_matrix("필터 A")
    filter_b = input_matrix("필터 B")
    pattern = input_matrix("패턴")

    score_a = calculate_mac(pattern=pattern, filter_data=filter_a)
    score_b = calculate_mac(pattern=pattern, filter_data=filter_b)

    result = decide_pattern(score_a=score_a, score_b=score_b)

    print("==== MAC 결과 ====")
    print(f"A 점수 : {score_a}")
    print(f"B 점수 : {score_b}")
    print(f"판정: {result}")

def main():
    while True:
        print()
        print("=== NPU 시뮬레이션 ===")
        print("1. 사용자 입력 (3X3)")
        print("2. data.json 분석")
        print("0. 종료")

        choice = input("선택 : ").strip()

        if choice == "1":
            run_user_mode()
        elif choice =="2":
            print("data.json run ")
        elif choice == "0":
            print("종료")
            break
        else:
            print("올바른 값을 입력하세요.")

if __name__ == "__main__":
    main()