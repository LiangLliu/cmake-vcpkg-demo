#include "pcl_point_types_demo.h"

#include <iostream>
#include <pcl/point_cloud.h>
#include <pcl/point_types.h>
#include <pcl/io/pcd_io.h>

int main() {
    pcl::PointCloud<pcl::PointXYZ>::Ptr cloud(new pcl::PointCloud <pcl::PointXYZ>);

    // 添加一些点到点云中
    cloud->width = 5;
    cloud->height = 1;
    cloud->is_dense = false;
    cloud->points.resize(cloud->width * cloud->height);

    for (size_t i = 0; i < cloud->points.size(); ++i) {
        cloud->points[i].x = 1024 * rand() / (RAND_MAX + 1.0f);
        cloud->points[i].y = 1024 * rand() / (RAND_MAX + 1.0f);
        cloud->points[i].z = 1024 * rand() / (RAND_MAX + 1.0f);
    }

    // 打印 PCL 点云数据
    std::cout << "PCL PointCloud:" << std::endl;
    for (const auto &point: cloud->points) {
        std::cout << "    " << point.x << " " << point.y << " " << point.z << std::endl;
    }

    // 保存点云到PCD文件
    pcl::io::savePCDFileASCII("./sample_cloud.pcd", *cloud);
    std::cout << "Saved " << cloud->points.size() << " data points to sample_cloud.pcd." << std::endl;

    return 0;
}
