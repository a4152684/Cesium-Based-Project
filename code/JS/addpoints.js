/*
 * @Description:
 * @Author: longchen
 * @Date: 2020-07-26 11:02:48
 * @LastEditTime: 2020-07-28 08:40:32
 */
var viewer = new Cesium.Viewer("cesiumContainer");
var scene = viewer.scene;

function display() {
    var points = scene.primitives.add(
        new Cesium.PointPrimitiveCollection()
    );
    var center = Cesium.Cartesian3.fromDegrees(114.367581, 30.534067, 0);
    points.modelMatrix = Cesium.Transforms.eastNorthUpToFixedFrame(center);
    $.getJSON("../data/武汉大学-车载点云/180614_072532_1.json", function (result) {
        $.each(result, function (i, point) {
            if (i > 1e6) {
                return false;
            }
            points.add({
                position: new Cesium.Cartesian3(point.X / 1000, point.Y / 1000, point.Z / 1000),
                color: Cesium.Color.GREEN
            })
        });
        alert('绘制完毕');
    })
    viewer.camera.flyTo({
        destination: Cesium.Cartesian3.fromDegrees(114.367581, 30.534067, 1000),
    });
}

function del() {
    scene.primitives.removeAll();
    viewer.camera.flyHome();
}

document.getElementById('display').onclick = function () {
    display();
}

document.getElementById('delete').onclick = function () {
    del();
}