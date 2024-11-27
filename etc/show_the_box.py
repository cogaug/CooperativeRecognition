import matplotlib.pyplot as plt
import matplotlib.patches as patches

def calculate_iou(box1, box2):
    x_left = max(box1[0][0], box2[0][0])
    y_top = max(box1[0][1], box2[0][1])
    x_right = min(box1[1][0], box2[1][0])
    y_bottom = min(box1[1][1], box2[1][1])

    if x_right < x_left or y_bottom < y_top:
        return 0.0

    intersection_area = (x_right - x_left) * (y_bottom - y_top)
    box1_area = (box1[1][0] - box1[0][0]) * (box1[1][1] - box1[0][1])
    box2_area = (box2[1][0] - box2[0][0]) * (box2[1][1] - box2[0][1])
    union_area = box1_area + box2_area - intersection_area
    return intersection_area / union_area

def plot_bounding_boxes(actual_box, predicted_box):
    fig, ax = plt.subplots()

    actual_rect = patches.Rectangle(
        (actual_box[0][0], actual_box[0][1]),
        actual_box[1][0] - actual_box[0][0],
        actual_box[1][1] - actual_box[0][1],
        linewidth=2,
        edgecolor='blue',
        facecolor='none',
        label="Actual Box"
    )

    predicted_rect = patches.Rectangle(
        (predicted_box[0][0], predicted_box[0][1]),
        predicted_box[1][0] - predicted_box[0][0],
        predicted_box[1][1] - predicted_box[0][1],
        linewidth=2,
        edgecolor='red',
        facecolor='none',
        label="Predicted Box"
    )

    ax.add_patch(actual_rect)
    ax.add_patch(predicted_rect)
    
    # 축의 한계 설정
    ax.set_xlim(min(actual_box[0][0], predicted_box[0][0]) - 1, max(actual_box[1][0], predicted_box[1][0]) + 1)
    ax.set_ylim(min(actual_box[0][1], predicted_box[0][1]) - 1, max(actual_box[1][1], predicted_box[1][1]) + 1)
    
    ax.set_aspect('equal')
    plt.legend()
    plt.title("Bounding Box Comparison")
    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")
    plt.show()

# 예시: 실제 박스와 예측 박스 좌표 설정
actual_box = [[520.7 - 5.20 / 2, 240.93 - 2.626 / 2], [520.7 + 5.20 / 2, 240.93 + 2.626 / 2]]
predicted_box = [[520.16 - 2.6, 240.47 - 1.3], [520.16 + 2.6, 240.47 + 1.3]]

# IoU 계산
iou = calculate_iou(actual_box, predicted_box)
print(f"IoU: {iou}")

# 바운딩 박스 시각화
plot_bounding_boxes(actual_box, predicted_box)
