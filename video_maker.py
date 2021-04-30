import cv2
import numpy as np
from scipy.interpolate import interp1d


def boxes(img_arr, predictions, headcount=False, faces_on=False):
    out_arr = []

    for img, pred in zip(img_arr, predictions):
        if faces_on:
            for p in pred:
                # img = np.copy(img)
                cv2.rectangle(img, (p[1][1], p[1][2]), (p[1][3], p[1][0]), (0, 0, 255), 2)
                cx = p[1][1]
                cy = p[1][2] + 12

                cv2.putText(img, p[0], (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

        if headcount:
            cv2.putText(img, "Head count: " + str(len(pred)),
                        (5, 30), cv2.FONT_HERSHEY_TRIPLEX, 1, (60, 20, 220))

        out_arr.append(img)

    out_arr = np.asarray(out_arr)
    return out_arr


def emotion_boxes(img_arr, predictions, headcount=False, faces_on=False):
    emotions_lapse = []
    out_arr = []
    if img_arr is not None:
        for img, pred in zip(img_arr, predictions):
            buf = np.zeros(7)
            for p in pred:
                buf = np.add(buf, p[0])
            emotions_lapse.append(buf)
            img = augment_frame(img, emotions_lapse, len(pred), len(img_arr), faces_on)
            if headcount:
                cv2.putText(img, "Head count: " + str(len(pred)),
                            (5, 30), cv2.FONT_HERSHEY_TRIPLEX, 1, (60, 20, 220))
            out_arr.append(img)
        return out_arr

    for pred in predictions:
        buf = np.zeros(7)
        for p in pred:
            buf = np.add(buf, p[0])
        emotions_lapse.append(buf)
        img = np.zeros((400, 1920, 3), dtype=np.uint8)
        img = augment_frame(img, emotions_lapse, len(pred), len(predictions), faces_on)
        if headcount:
            cv2.putText(img, "Head count: " + str(len(pred)),
                        (5, 30), cv2.FONT_HERSHEY_TRIPLEX, 1, (60, 20, 220))
            # cv2.imshow('sup', img)
            # cv2.waitKey(0)
        out_arr.append(img)
    return out_arr


def optimized_boxes(original_video_img_array, predictions, headcount=False, faces_on=False):
    emotions_lapse = []
    out_arr = []
    em_labels = np.array(['ANGRY', 'DISGUST', 'FEAR', 'HAPPY', 'SAD', 'SURPRISE', 'NEUTRAL'])
    if original_video_img_array is not None:
        for img, pred in zip(original_video_img_array, predictions):
            buf = np.zeros(7)
            for p in pred:
                zeros = np.zeros(7)
                zeros[np.argwhere(em_labels == p[1])] = 1
                buf = np.add(buf, zeros)
            emotions_lapse.append(buf)
            img = augment_frame(img, emotions_lapse, len(pred), len(original_video_img_array), faces_on)
            if headcount:
                cv2.putText(img, "Head count: " + str(len(pred)),
                            (5, 30), cv2.FONT_HERSHEY_TRIPLEX, 1, (60, 20, 220))
            out_arr.append(img)
        return out_arr

    for pred in predictions:
        buf = np.zeros(7)
        for p in pred:
            zeros = np.zeros(7)
            zeros[np.argwhere(em_labels == p[1])] = 1
            buf = np.add(buf, zeros)
        emotions_lapse.append(buf)
        img = np.zeros((400, 1920, 3), dtype=np.uint8)
        img = augment_frame(img, emotions_lapse, len(pred), len(predictions), faces_on)
        if headcount:
            cv2.putText(img, "Head count: " + str(len(pred)),
                        (5, 30), cv2.FONT_HERSHEY_TRIPLEX, 2, (60, 20, 220))
            # cv2.imshow('sup', img)
            # cv2.waitKey(0)
        out_arr.append(img)
    return out_arr


def render(dir, filename, frames, num_fps):
    string = dir + "/" + filename

    writer = cv2.VideoWriter(
        string,
        cv2.VideoWriter_fourcc(*'MP4V'),  # codec
        num_fps,  # fps
        (frames[0].shape[1], frames[0].shape[0]))  # width, height
    for frame in (frames):
        writer.write(frame)
    writer.release()
    # cv2.destroyAllWindows()
    return string


def optimized_render(dir, filename, predictions, num_fps, metrics_lapse, headcount=False):
    string = dir + "/" + filename
    em_labels = np.array(['ANGRY', 'DISGUST', 'FEAR', 'HAPPY', 'SAD', 'SURPRISE', 'NEUTRAL'])
    positive_emotions = [3, 5]
    active_emotions = [0, 3, 5]
    head_count = 0
    max_poins_in_plot = 250
    pop_metrics_lapse = True
    if not metrics_lapse:
        pop_metrics_lapse = False
    # metrics_lapse = []

    writer = cv2.VideoWriter(
        string,
        cv2.VideoWriter_fourcc(*'MP4V'),  # codec
        num_fps,  # fps
        (1920, 400))  # width, height
    for pred in predictions:
        affection_coef = 0
        attention_coef = 0
        valence_coef = 0
        buf = np.zeros(7)
        for p in pred:
            zeros = np.zeros(7)
            zeros[np.argwhere(em_labels == p[1])] = 1
            buf = np.add(buf, zeros)
        head_count = len(pred)
        if head_count:
            attention_coef = np.max(buf) / head_count

            for i in positive_emotions:
                affection_coef += buf[i] / head_count

            for i in active_emotions:
                valence_coef += buf[i] / head_count

        metrics_lapse.append([attention_coef, affection_coef, valence_coef])
        if pop_metrics_lapse or len(metrics_lapse) > max_poins_in_plot:
            metrics_lapse.pop(0)
        # metrics_lapse.append(buf)
        img = np.zeros((400, 1920, 3), dtype=np.uint8)
        changed_metric_lapse = metrics_lapse
        new_max_points_in_plot = max_poins_in_plot
        if head_count > 3:
            transposed_metrics_lapse = np.array(metrics_lapse).T
            smooth_metric_lapse = []
            for metric in transposed_metrics_lapse:
                f = interp1d(np.linspace(1, metric.shape[0]+1, num=metric.shape[0]), metric, kind='cubic')
                smooth_metric_lapse.append(f(np.linspace(1, metric.shape[0], num=metric.shape[0]*5)))
            smooth_metric_lapse = np.array(smooth_metric_lapse).T
            changed_metric_lapse = smooth_metric_lapse.tolist()
            new_max_points_in_plot = max_poins_in_plot*5
        img = augment_frame_metrics_only(img, changed_metric_lapse, head_count, new_max_points_in_plot)
        if headcount:
            cv2.putText(img, "Head count: " + str(head_count),
                        (5, 40), cv2.FONT_HERSHEY_TRIPLEX, 2, (60, 20, 220))
        writer.write(img)
    writer.release()
    # cv2.destroyAllWindows()
    return string, metrics_lapse


def augment_frame(img, emotions_lapse, head_count, len_img_arr=None, faces_on=False):

    class_labels = ['ANGRY', 'DISGUST', 'FEAR', 'HAPPY', 'SAD', 'SURPRISE', 'NEUTRAL']
    affection_coef = 0
    valance_coef = 0
    positive_emotions = [3, 5]
    active_emotions = [0, 3, 5]

    display_img = np.copy(img)
    if not faces_on:
        display_img = np.zeros_like(display_img)
        display_img = np.resize(display_img, (400, 1920, 3))

    shift = 0
    nemotions_lapse = np.asarray(emotions_lapse) * display_img.shape[0] / (2 * head_count)
    x = range(1, len(emotions_lapse) + 1)
    x = np.asarray(x)

    unchanged_angry_scores = np.asarray(emotions_lapse)[:, 0]
    unchanged_disgust_scores = np.asarray(emotions_lapse)[:, 1]
    unchanged_fear_scores = np.asarray(emotions_lapse)[:, 2]
    unchanged_happy_scores = np.asarray(emotions_lapse)[:, 3]
    unchanged_sad_scores = np.asarray(emotions_lapse)[:, 4]
    unchanged_surprise_scores = np.asarray(emotions_lapse)[:, 5]
    unchanged_neutral_scores = np.asarray(emotions_lapse)[:, 6]

    attention_coef = np.max(np.max(np.flip(emotions_lapse)[0, :], axis=0)) / head_count

    for i in positive_emotions:
        affection_coef += np.flip(emotions_lapse)[0, i] / head_count
    for i in active_emotions:
        valance_coef += np.flip(emotions_lapse)[0, i] / head_count

    # attention_coef = (np.max(emotions_count)) / head_count
    # attention_coef = np.mean(emotions_count) / np.max(emotions_count)

    scale = display_img.shape[1] - 30
    if len_img_arr is not None:
        scale = scale / len_img_arr
    x = x * scale + 15

    shift = display_img.shape[0] / 2 - 10
    angry_scores = shift + nemotions_lapse[:, 0]
    disgust_scores = shift + nemotions_lapse[:, 1]
    fear_scores = shift + nemotions_lapse[:, 2]
    happy_scores = shift - nemotions_lapse[:, 3]
    sad_scores = shift + nemotions_lapse[:, 4]
    surprise_scores = shift - nemotions_lapse[:, 5]
    neutral_scores = shift - nemotions_lapse[:, 6]

    # emotions_scores = [angry_scores, disgust_scores, fear_scores,
    #                    happy_scores, sad_scores, surprise_scores, neutral_scores]

    plot = np.vstack((x, angry_scores)).astype(np.int32).T
    cv2.polylines(display_img, [plot], isClosed=False, thickness=2, color=(0, 0, 255))
    cord = (plot[len(plot) - 1][0], plot[len(plot) - 1][1])
    cv2.putText(display_img,
                class_labels[0] + " " + str(int(np.flip(unchanged_angry_scores)[0])),
                cord, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)

    plot = np.vstack((x, disgust_scores)).astype(np.int32).T
    cv2.polylines(display_img, [plot], isClosed=False, thickness=2, color=(0, 255, 0))
    cord = (plot[len(plot) - 1][0], plot[len(plot) - 1][1])
    cv2.putText(display_img,
                class_labels[1] + " " + str(int(np.flip(unchanged_disgust_scores)[0]))
                , cord, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)

    plot = np.vstack((x, fear_scores)).astype(np.int32).T
    cv2.polylines(display_img, [plot], isClosed=False, thickness=2, color=(255, 255, 255))
    cord = (plot[len(plot) - 1][0], plot[len(plot) - 1][1])
    cv2.putText(display_img,
                class_labels[2] + " " + str(int(np.flip(unchanged_fear_scores)[0]))
                , cord, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    plot = np.vstack((x, happy_scores)).astype(np.int32).T
    cv2.polylines(display_img, [plot], isClosed=False, thickness=2, color=(0, 255, 255))
    cord = (plot[len(plot) - 1][0], plot[len(plot) - 1][1])
    cv2.putText(display_img,
                class_labels[3] + " " + str(int(np.flip(unchanged_happy_scores)[0]))
                , cord, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)

    plot = np.vstack((x, sad_scores)).astype(np.int32).T
    cv2.polylines(display_img, [plot], isClosed=False, thickness=2, color=(153, 153, 255))
    cord = (plot[len(plot) - 1][0], plot[len(plot) - 1][1])
    cv2.putText(display_img,
                class_labels[4] + " " + str(int(np.flip(unchanged_sad_scores)[0]))
                , cord, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (153, 153, 255), 1)

    plot = np.vstack((x, surprise_scores)).astype(np.int32).T
    cv2.polylines(display_img, [plot], isClosed=False, thickness=2, color=(153, 0, 76))
    cord = (plot[len(plot) - 1][0], plot[len(plot) - 1][1])
    cv2.putText(display_img,
                class_labels[5] + " " + str(int(np.flip(unchanged_surprise_scores)[0]))
                , cord, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (153, 0, 76), 1)

    plot = np.vstack((x, neutral_scores)).astype(np.int32).T
    cv2.polylines(display_img, [plot], isClosed=False, thickness=2, color=(96, 96, 96))
    cord = (plot[len(plot) - 1][0], plot[len(plot) - 1][1])
    cv2.putText(display_img,
                class_labels[6] + " " + str(int(np.flip(unchanged_neutral_scores)[0]))
                , cord, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (96, 96, 96), 1)

    cv2.putText(display_img, "Attention coef: " + str(round(attention_coef, 2)),
                (300, 30), cv2.FONT_HERSHEY_TRIPLEX, 1, (60, 20, 220))

    cv2.putText(display_img, "Arousal coef: " + str(round(affection_coef, 2)),
                (1500, 30), cv2.FONT_HERSHEY_TRIPLEX, 1, (60, 20, 220))

    cv2.putText(display_img, "Valance coef: " + str(round(valance_coef, 2)),
                (800, 30), cv2.FONT_HERSHEY_TRIPLEX, 1, (60, 20, 220))

    return display_img


def augment_frame_metrics_only(img, metrics_lapse, head_count, len_img_arr=None, faces_on=False):

    class_labels = ['ANGRY', 'DISGUST', 'FEAR', 'HAPPY', 'SAD', 'SURPRISE', 'NEUTRAL']
    metrics_labels = ['Attention', 'Affection', 'Valence']
    # affection_coef = 0
    # valence_coef = 0
    positive_emotions = [3, 5]
    active_emotions = [0, 3, 5]

    display_img = np.copy(img)
    if not faces_on:
        display_img = np.zeros_like(display_img)
        display_img = np.resize(display_img, (400, 1920, 3))

    shift = 0
    x = range(1, len(metrics_lapse) + 1)
    # newx = np.linspace(1, len(metrics_lapse), num=len(metrics_lapse)*10)
    x = np.asarray(x)
    nmetrics_lapse = np.asarray(metrics_lapse) * display_img.shape[0] / 1.5

    unchanged_attention_scores = np.asarray(metrics_lapse)[:, 0]
    unchanged_affection_scores = np.asarray(metrics_lapse)[:, 1]
    unchanged_valence_scores = np.asarray(metrics_lapse)[:, 2]

    # attention_coef = np.max(np.max(np.flip(frame_prediction)[0], axis=0)) / head_count
    #
    # for i in positive_emotions:
    #     affection_coef += np.flip(frame_prediction)[i] / head_count
    # for i in active_emotions:
    #     valence_coef += np.flip(frame_prediction)[i] / head_count
    #
    # metrics_lapse.append([attention_coef, affection_coef, valence_coef])


    # attention_coef = (np.max(emotions_count)) / head_count
    # attention_coef = np.mean(emotions_count) / np.max(emotions_count)

    scale = display_img.shape[1] - 30
    if len_img_arr is not None:
        scale = scale / len_img_arr
    x = x * scale + 15

    shift = display_img.shape[0] - 10
    attention_scores = shift - nmetrics_lapse[:, 0]
    affection_scores = shift - nmetrics_lapse[:, 1]
    valence_scores = shift - nmetrics_lapse[:, 2]

    # emotions_scores = [angry_scores, disgust_scores, fear_scores,
    #                    happy_scores, sad_scores, surprise_scores, neutral_scores]

    plot = np.vstack((x, attention_scores)).astype(np.int32).T
    cv2.polylines(display_img, [plot], isClosed=False, thickness=2, color=(0, 0, 255))
    cord = (plot[len(plot) - 1][0], plot[len(plot) - 1][1])
    cv2.putText(display_img,
                metrics_labels[0] + " " + str(round(np.flip(unchanged_attention_scores)[0], 2)),
                cord, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)

    plot = np.vstack((x, affection_scores)).astype(np.int32).T
    cv2.polylines(display_img, [plot], isClosed=False, thickness=2, color=(0, 255, 0))
    cord = (plot[len(plot) - 1][0], plot[len(plot) - 1][1])
    cv2.putText(display_img,
                metrics_labels[1] + " " + str(round(np.flip(unchanged_affection_scores)[0], 2))
                , cord, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)

    plot = np.vstack((x, valence_scores)).astype(np.int32).T
    cv2.polylines(display_img, [plot], isClosed=False, thickness=2, color=(255, 255, 255))
    cord = (plot[len(plot) - 1][0], plot[len(plot) - 1][1])
    cv2.putText(display_img,
                metrics_labels[2] + " " + str(round(np.flip(unchanged_valence_scores)[0], 2))
                , cord, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    cv2.putText(display_img, "Attention coef: " + str(round(metrics_lapse[-1][0], 2)),
                (300, 60), cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 0, 255))

    cv2.putText(display_img, "Arousal coef: " + str(round(metrics_lapse[-1][1], 2)),
                (1500, 60), cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 255, 0))

    cv2.putText(display_img, "Valance coef: " + str(round(metrics_lapse[-1][2], 2)),
                (800, 60), cv2.FONT_HERSHEY_TRIPLEX, 1, (255, 255, 255))

    return display_img
